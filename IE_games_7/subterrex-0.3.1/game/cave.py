"""Represents a cave"""

import math
import pygame
import random
import time

import serge.actor
import serge.visual
import serge.blocks.visualblocks
import serge.blocks.visualeffects
import serge.blocks.fractals
import serge.blocks.lsystem
from serge.simplevecs import Vec2d

from theme import G, theme
import common 
import light
import climbing
import creator
import flare
import crystal
import tree

class OutOfRange(Exception): """The position was not in the board"""

# Constants for water types
W_SOURCE = 3
W_FALL_CENTER = 10
W_FALL_CENTER_FLAT = 17
W_FLAT = 16
W_CORNER = 19
W_FALL_EDGE = 26
W_FALL_EDGE_FLAT = 20


class Cave(serge.actor.Actor):
    """Represents the cave"""

    _sprite_cache = {}
    _generated_cache = False
    
    def __init__(self, name, tag, tilemap, fractal_layers):
        """Initialise the actor"""
        super(Cave, self).__init__(tag, name)
        self.tilemap = tilemap
        self.fractal_layers = fractal_layers
        #
        # Create a layout to help position items
        self.tw, self.th = G('cell-size')
        cols, rows = self.tilemap.getSize()
        w, h = self.tw*cols, self.th*rows
        self.visual = serge.visual.SurfaceDrawing(w, h)
        self.layout = serge.blocks.layout.BaseGrid('grid', 'grid', (cols, rows), w, h)
        self.water_falls_locations = []  # Where water is falling on a surface (and so would make a noise)

    def addedToWorld(self, world):
        """Added the board to the world"""
        super(Cave, self).addedToWorld(world)
        self.world = world
        self.manager = world.findActorByName('behaviours')
        self.camera = serge.engine.CurrentEngine().getRenderer().getCamera()
        self.generateSpriteCache()
        #
        # Light
        self.light = serge.blocks.utils.addActorToWorld(world,
            light.LightMask('light', 'light', G('light-mask-colour')),
            center_position=G('cave-position'),
            layer_name='light')
        #
        # Remain invisible until the light is ready
        self.visible = False
                                
    def createVisual(self, backgrounds, trees, add_mask=True):
        """Create the visual for the board"""
        #
        # We can either use fix or parallax background. If we use parallax then we need to
        # add actors to the world. If we are using fixed then we can just render them directly
        if G('cave-parallax-background'):
            for background in backgrounds:
                self.world.addActor(background)
                self.manager.assignBehaviour(background, 
                    serge.blocks.behaviours.ParallaxMotion(self.camera, (1.0, G('cave-parallax-amount'))), 'parallax')
        else:
            for background in backgrounds:
                background.visual.renderTo(0, self.visual.getSurface(), background.getOrigin())
        #
        # Trees
        if G('cave-tree-parallax-background'):
            for tree in trees:
                self.world.addActor(tree)
                self.manager.assignBehaviour(tree, 
                    serge.blocks.behaviours.ParallaxMotion(self.camera, (1.0, G('cave-tree-parallax-amount'))), 'parallax')
        else:
            for tree in trees:
                tree.visual.renderTo(0, self.visual.getSurface(), tree.getOrigin())
        #
        # Now the main pieces
        cols, rows = self.tilemap.getSize()
        for layer in self.tilemap.getLayers():
            for row in range(rows):
                for col in range(cols):
                    if layer in self.tilemap.getLayersForTile((col, row)):
                        sprite = random.choice(self._sprite_cache[layer.name])
                        x, y = self.layout.getCoords((col, row))
                        cx, cy = x-sprite.width/2, y-sprite.height/2
                        cell_no = layer.tiles[row][col]
                        if hasattr(sprite, 'setCell'):
                            sprite.setCell(abs(cell_no)-1)
                        sprite.setHorizontalFlip(cell_no < 0)
                        sprite.renderTo(0, self.visual.getSurface(), (cx, cy))
        #
        self.visual.setSurface(self.visual.getSurface().convert_alpha())
        
    def createActors(self, add_physics):
        """Create the actors for the cave"""
        self.log.debug('Creating actors for the cave')
        #
        # Clear old actors
        self.world.clearActorsWithTags(['rock'])
        #
        # Now create an actor for each piece of rock
        rock_layer = self.tilemap.getLayer('rock')
        rock_x, rock_y = G('cell-size')
        cols, rows = self.tilemap.getSize()
        created = skipped = 0
        #
        for row in range(rows):
            for col in range(cols):
                if self._tileRequiresActor((col, row), rock_layer):
                    created += 1
                    x, y = self.layout.getCoords((col, row))
                    #
                    # Create a rock
                    rock = climbing.Climbable('rock', 'rock-%d-%d' % (col, row))
                    rock.visual = serge.blocks.visualblocks.Rectangle((rock_x, rock_y), (255, 255, 0))
                    if add_physics:
                        rock.setPhysical(serge.physical.PhysicalConditions(mass=50.0, fixed=True, visual_size=True, 
                            group=climbing.G_SURFACES, elasticity=0.1, friction=0.8))
                    rock.setLayerName('main')
                    rock.moveTo(x, y)
                    #
                    # Don't want to actually draw the rock
                    rock.visible = False
                    #
                    # Collect click events
                    rock.linkEvent(serge.events.E_LEFT_CLICK, self.rockClick, (rock, common.E_ROCK_CLICKED))
                    rock.linkEvent(serge.events.E_RIGHT_CLICK, self.rockClick, (rock, common.E_ROCK_RIGHT_CLICKED))
                    #
                    self.world.addActor(rock)
                else:
                    skipped += 1
        #
        self.log.info('Cave created %d actors (optimised from %d)' % (created, created+skipped))
        
    def _tileRequiresActor(self, (col, row), rock_layer):
        """Return True if the location requires an actor to be created
        
        This is an optimization to avoid creating actors which are not needed because
        they are embeded in the main rock and would never come into contact with
        the player.
        
        """
        #
        # Is this a rock at all?
        if rock_layer not in self.tilemap.getLayersForTile((col, row)):
            return False
        #
        cols, rows = self.tilemap.getSize()
        #
        # Look to see that at least one neighbour is missing
        for dc, dr in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
            ac = col+dc
            ar = row+dr
            if 0 <= ac < cols and 0 <= ar < rows:
                if rock_layer not in self.tilemap.getLayersForTile((ac, ar)):
                    return True
        #
        # Ok, so all neighbours are occupied so the player will never touch this
        return False


    def rockClick(self, obj, (rock, event)):
        """A rock was clicked on"""
        self.log.debug('Clicked on %s (%s)' % (rock.getNiceName(), event))
        self.processEvent((event, rock))
        
    def getSprite(self, layer):
        """Return the sprite for a layer"""
        #
        # Return the relevant sprite to draw
        if layer not in self.fractal_layers:
            return serge.visual.Sprites.getItem(layer)
        else:
            #
            # Generate a fractal shape for the block
            w, h = G('cell-size')[0]*G('fractal-overstuff'), G('cell-size')[1]*G('fractal-overstuff')
            sprite = serge.visual.SurfaceDrawing(2*w, 2*h)
            points = [(w/2, h/2), (3*w/2, h/2), (3*w/2, 3*h/2), (w/2, 3*h/2), (w/2, h/2)]
            fractal = serge.blocks.fractals.fractalShape(points, G('fractal-num-steps'), G('fractal-distance'), G('fractal-decay'))
            #
            # Draw as a sprite
            pygame.draw.polygon(sprite.getSurface(), self.fractal_layers[layer], fractal)
            #
            if G('fractal-blur'):
                sprite.setSurface(serge.blocks.visualeffects.gaussianBlur(sprite.getSurface(), G('fractal-blur')))
            #
            return sprite
    
    def generateSpriteCache(self):
        """Generate a cache of fractal sprites"""
        if self._generated_cache:
            return
        for layer in G('cave-fractals'):
            self._sprite_cache[layer] = []
            for idx in range(G('fractal-sprite-cache-size')):
                self._sprite_cache[layer].append(self.getSprite(layer))
        for layer in G('cave-sprites'):
            if layer not in G('cave-fractals'):
                self._sprite_cache[layer] = [serge.visual.Sprites.getItem(layer)]
        self.__class__._generated_cache = True
                            
    def updateActor(self, interval, world):
        """Update the actor"""
        super(Cave, self).updateActor(interval, world)
        #
        if self.light.isReady():
            self.visible = True
        #
        # Handle foam
        for source in self.water_drops:
            if random.random() < G('foam-probability'):
                self.log.debug('Creating some foam in fall %s' % (source,))
                foam = serge.blocks.utils.addSpriteActorToWorld(world, 'foam', 'foam', 
                    sprite_name='foam', layer_name='foam', center_position=self.layout.getCoords(source[0]))
                fx, fy = self.layout.getCoords(source[-1])
                self.manager.assignBehaviour(foam,
                    serge.blocks.behaviours.MoveTowardsPoint(
                        (fx+random.randrange(*G('foam-x-jitter')), fy),
                        y_speed=random.randrange(*G('foam-speed')), remove_when_there=True),
                    'falling-foam')
            
    def calculateWater(self, source, amount, moss_layer):
        """Add some water to the cave"""
        self.log.info('Calculating water at %s with amount %s' % (source, amount))
        #
        x, y = source
        self.processWater((x, y), amount, moss_layer, W_SOURCE, +1)
        
    def processWater(self, (x, y), amount, moss_layer, water_type, direction):
        """Process a water drop"""
        #
        # Set this point as water
        water = self.tilemap.getLayer('water')
        water.tiles[y][x] = water_type*direction
        self.log.debug('Water flowing at %d, %d (%s) direction %d' % (x, y, water.tiles[y][x], direction))
        #
        # Store drops
        if water_type == W_SOURCE:
            self.water_drops.append([(x,y)])
        elif water_type in (W_FALL_CENTER, W_FALL_CENTER_FLAT):
            self.water_drops[-1].append((x,y))
        elif water_type in (W_FALL_EDGE, W_FALL_EDGE_FLAT):
            self.water_drops[-1].append((x+direction*G('foam-x-offset'),y))
        #
        # Water exhausted?
        if amount <= 0:
            return
        #
        # Ok so move water
        rock = self.tilemap.getLayer('rock')
        #
        # Down, right, left, up
        if y < len(rock.tiles)-1 and not rock.tiles[y+1][x]:
            #
            # Falling down
            if water_type == W_FLAT:
                water.tiles[y][x] = W_CORNER*direction
                self.log.debug('Flipped to %d' % water.tiles[y][x])
            if water_type not in (W_FALL_CENTER, W_FALL_CENTER_FLAT, W_FALL_EDGE, W_FALL_EDGE_FLAT):
                self.water_drops.append([])
            self.processWater((x, y+1), amount-1, moss_layer, (W_FALL_CENTER if water_type in (W_FALL_CENTER, W_SOURCE) 
                    else W_FALL_EDGE), direction)
        elif y < len(rock.tiles)-1:
            #
            # Not falling - we are blocked by something so go horizontally in some way
            if water_type == W_FALL_CENTER:
                water.tiles[y][x] = W_FALL_CENTER_FLAT*direction
                self.log.debug('Flipped to %d' % water.tiles[y][x])
                self.water_falls_locations.append(self.layout.getCoords((x, y)))
            elif water_type == W_FALL_EDGE:
                water.tiles[y][x] = W_FALL_EDGE_FLAT*direction
                self.log.debug('Flipped to %d' % water.tiles[y][x])
                self.water_falls_locations.append(self.layout.getCoords((x, y)))
            if G('do-moss'):
                moss_layer.tiles[y+1][x] = 1
            if x < len(rock.tiles[y])-1 and not rock.tiles[y][x+1] and not water.tiles[y][x+1]:
                self.processWater((x+1, y), amount-1, moss_layer, W_FLAT, +1)
            if x > 0 and not rock.tiles[y][x-1] and not water.tiles[y][x-1]:
                self.processWater((x-1, y), amount-1, moss_layer, W_FLAT, -1)
 
    def createSurface(self, width):
        """Add a layer for the surface"""
        surface = self.tilemap.getLayer('surface')         
        cols, rows = surface.getSize()
        for row in range(width):
            for col in range(cols):
                surface.tiles[row][col] = 1
            
        
    def getVisualVectorTo(self, tiles, (x, y), (tx, ty), step_size):
        """Return the offset vector to a target if we can see if or False if we cannot"""
        #
        # Determine offset between us and the target
        my_location = Vec2d(x, y)
        vector_to = Vec2d(tx, ty) - my_location
        step = vector_to.normalized()*step_size
        steps = int(vector_to.length/step_size)    
        #
        # Move from me to the player checking if there are barriers in the way
        for idx in range(steps):
            check = my_location + step*idx
            cx, cy = self.layout.getLocation(check)
            item = tiles[cy][cx]
            if item:
                return None
        else:
            return vector_to

    def calculateLight(self, lights, ambient, mask):
        """Calculate the light field for the cave"""
        #
        # Ray trace from each square to each light source
        self.log.info('Starting light evaluation')
        start_time = time.time()
        #
        self.light_field = cells = []
        directions = []
        max_evaluation_distance = G('max-evaluation-distance', 'light')
        tiles = self.tilemap.getLayer('rock').tiles
        cell_size = 16.0#G('cell-size')[0]/2.0
        for y, row in enumerate(tiles):
            cells.append([])
            directions.append([])
            for x, item in enumerate(row):
                illumination = r = g = b = 0
                distances = []
                for light in lights:
                    dr, dg, db = light.colour
                    px, py = self.layout.getCoords((x, y))
                    if abs(light.x-px) + abs(light.y-py) <= max_evaluation_distance:
                        if light.light_type == 'light':
                            vector_to = self.getVisualVectorTo(tiles, (px, py), (light.x, light.y), cell_size)
                        else:
                            vector_to = Vec2d(light.x, light.y) - Vec2d((px, py))
                        if vector_to is not None:
                            d = vector_to.length
                            illumination += light.strength * math.exp(-d/light.distance)
                            r += dr/255*light.strength * math.exp(-d/light.distance)
                            g += dg/255*light.strength * math.exp(-d/light.distance)
                            b += db/255*light.strength * math.exp(-d/light.distance)
                            #
                            distances.append((d, vector_to))
                illumination = min(255, illumination+ambient)
                cells[-1].append((illumination, min(255,r), min(255,g), min(255,b)))
                #
                if distances:
                    distances.sort()
                    directions[-1].append(-distances[0][1].get_angle_degrees())
                else:
                    directions[-1].append(None)
        #
        # Handle the crystals
        crystals = self.world.findActorsByTag('crystal')
        for crystal in crystals:
            cx, cy = self.layout.getLocation((crystal.x, crystal.y))
            try:
                nr, ng, nb, na = cells[cy][cx]
            except IndexError:
                self.log.debug('Cystal %s is outside the viewable area (%s, %s)' % (self.getNiceName(), cy, cx))
            else:
                crystal.updateLighting(cells, (cx, cy))
        #
        # Update the mask
        locations = list(self.tilemap.getLayer('rock').iterCellLocations())
        #
        for cx, cy in locations:
            for repeat in range(1):
                x, y = self.layout.getCoords((cx, cy))
                r,g,b,a = 255,255,255,255#surface.get_at((x, y))
                light, r, g, b = cells[cy][cx]
                sprite = G('cell-size'), (r, g, b, light)
                mask.addSource((x, y), sprite)
        #
        self.log.info('Completed light evaluation (%5.2f s)' % (time.time()-start_time))
                        
    def getStartPosition(self):
        """Return a suitable start position"""
        cx, cy = random.choice(list(self.tilemap.getLayer('rock').iterCellLocations()))
        if self.tilemap.getLayer('rock').tiles[cy][cx]:
            #
            # Ooops, this is a rock
            return self.getStartPosition()
        else:
            return self.layout.getCoords((cx, cy))
    
    @classmethod        
    def generateCaveMap(cls, world, add_physics=True, random_seed=None):
        """Generate a map and add to the world"""
        cls.log.info('Generating a new cave')
        #
        # Create cave
        generated_cave = creator.CA_CaveFactory(G('cave-height')-G('surface-rows')-1, 
                G('cave-width'), G('cave-probability'), random_seed)
        generated_cave.gen_map()
        entrance = generated_cave.add_entrance(G('surface-rows'), G('entrance-width'), G('entrance-buffer'))
        exit = generated_cave.add_exit(G('exit-width'), G('exit-buffer'))
        #
        cave_map = serge.blocks.tiled.TileMap()
        water = cave_map.addLayer(serge.blocks.tiled.Layer(cave_map, 'water', 'visual', 
            width=G('cave-width'), height=G('cave-height')))
        moss = cave_map.addLayer(serge.blocks.tiled.Layer(cave_map, 'moss', 'visual', 
            width=G('cave-width'), height=G('cave-height')))
        rocks = cave_map.addLayer(serge.blocks.tiled.Layer(cave_map, 'rock', 'visual', 
            tiles=generated_cave.get_map()))
        surface = cave_map.addLayer(serge.blocks.tiled.Layer(cave_map, 'surface', 'visual', 
            width=G('cave-width'), height=G('cave-height')))
        #
        # Show cave
        new_cave = serge.blocks.utils.addActorToWorld(world,
            cls('cave', 'cave', cave_map, G('cave-fractals')),
            layer_name='main',
            center_position=G('cave-position'))
        #
        # Do water
        num_water_sources = int(random.triangular(*G('number-sources')))
        cls.log.info('Adding %d water sources' % num_water_sources)
        free_tiles = [(tx, ty) for tx, ty in rocks.getLocationsWithoutTile() if (G('surface-rows')+1 < ty < G('cave-height')*0.5)]
        cls.water_falls_locations = []
        cls.water_drops = []
        for i in range(num_water_sources):
            x, y = random.choice(free_tiles)
            v = G('water-amount')
            new_cave.calculateWater((x, y), v, moss)
        #
        # Remove trivial water vertical drops
        cls.water_drops = [drop for drop in cls.water_drops if len(drop) > 1]
        #
        # Trees
        trees = []
        num_trees = int(random.triangular(*G('number-trees')))
        free_tiles = [(tx, ty) for tx, ty in rocks.getLocationsWithoutTile() if (G('surface-rows')+1 < ty < G('cave-height')-5)]
        cls.log.info('Adding %d trees' % num_trees)
        tree_colour = tuple([random.randrange(0, c) for c in G('tree-colour')])
        for i in range(num_trees):
            t = serge.actor.Actor('tree', 'tree-%s' % i)
            t.setLayerName('trees')
            t.visual = tree.LTree(G('tree-size'), G('tree-size'), 'X', G('tree-rules'))
            t.visual.init_distance = G('tree-distance')
            t.visual.blur_amount = G('tree-blur')
            t.visual.circle_size = G('tree-circle-size')
            if G('tree-colour-randomize'):
                t.visual.colour = tree_colour
            else:
                t.visual.colour = G('tree-colour')
            #
            t.visual.doStep(G('tree-steps'))
            #
            # Find a place to put the tree
            cx, cy = random.choice(free_tiles)
            for offset in range(100):
                cls.log.debug('Checking tree at %s, %s' % (cx, cy))
                if cy >= len(rocks.tiles)-1:
                    break
                cy += 1
                if rocks.tiles[cy][cx]:
                    break
            #
            px, py = new_cave.layout.getCoords((cx, cy))
            py -= t.visual.height/2
            t.moveTo(px, py)
            cls.log.info('Added tree at %s, %s' % (t.x, t.y))
            trees.append(t)
        #
        # Background
        backgrounds = []
        for idx in range(G('cave-horizontal-screens')):
            for idy in range(G('cave-vertical-screens')):
                bg = serge.actor.Actor('bg', ('background-%d-%d' % (idx, idy)))
                bg.setSpriteName('surface' if idy == 0 else 'background')
                bg.setLayerName('background')
                bg.moveTo((2*idx+1)*G('screen-width')/2, (2*idy+1)*G('screen-height')/2)
                backgrounds.append(bg)
        #
        new_cave.createVisual(backgrounds, trees)
        new_cave.createActors(add_physics)
        #
        # Crystals
        num_crystals = int(random.triangular(*G('number-crystals')))
        cls.log.info('Adding %d crystals' % num_crystals)
        types = [crystal.FluorescentCrystal, crystal.LuminescentCrystal, crystal.NamedCrystal]
        for i in range(num_crystals):
            crystal_type = random.choice(types)
            c = crystal_type('crystal', 'crystal-%d' % i)
            c.moveTo(*new_cave.layout.getCoords(random.choice(free_tiles)))
            c.linkEvent(serge.events.E_REMOVED_FROM_WORLD, new_cave.crystalRemoved)
            world.addActor(c)
            cls.log.info('Added crystal at %s, %s' % (c.x, c.y))
        #
        # Let the crystals fall to where they may by running the simulation forward
        for zone in world.zones:
            zone.updatePhysics(10000)
        #
        # Lights
        new_cave.sources = []
        new_cave.addLight(new_cave.layout.getCoords(entrance), 
            G('entrance-light-colour'), G('entrance-light-strength'), G('entrance-light-distance'), update=False)
        new_cave.addLight((0, 0), 
            G('entrance-light-colour'), G('entrance-light-strength'), G('entrance-light-distance'), update=False)
        new_cave.addLight((G('screen-width'), 0), 
            G('entrance-light-colour'), G('entrance-light-strength'), G('entrance-light-distance'), update=False)
        new_cave.addLight(new_cave.layout.getCoords(exit), 
            G('exit-light-colour'), G('exit-light-strength'), G('exit-light-distance'), update=False)
        new_cave.updateLighting()
        #
        # Entrance and exit locations
        new_cave.exit_location = new_cave.layout.getCoords(exit)
        new_cave.entrance_location = new_cave.layout.getCoords(entrance)
        #
        return new_cave

    def crystalRemoved(self, obj, arg):
        """A crystal was removed"""
        self.updateLighting(need=light.U_NEED_RIGOROUS)
          
    def updateLighting(self, need=light.U_NEED_FAST):
        """Update the lighting"""
        #
        # Light
        self.light.clearSources(need)
        self.calculateLight(self.sources, G('light-ambient'), self.light)
    
    def addLight(self, (x, y), colour, strength, distance, flare_type=None, update=True):
        """Add a light at the given position"""
        self.log.debug('Adding light at %s, %s' % (x, y))
        self.sources.append(light.ColouredLight(x, y, strength, colour, distance))
        if flare_type:
            serge.blocks.utils.addActorToWorld(self.world, 
                flare.Flare('flare', 'flare-%d' % len(self.sources), flare_type),
                center_position=(x, y))
        if update:
            self.updateLighting()
        
