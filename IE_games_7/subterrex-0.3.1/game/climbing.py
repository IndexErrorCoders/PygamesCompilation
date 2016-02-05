"""Classes to help with climbing around"""

import pygame
import pymunk
Vec2d = pymunk.Vec2d
import math
import time

import serge.actor
import serge.blocks.actors
import serge.blocks.utils
import serge.blocks.visualblocks

from theme import G as GG, theme

class NotClimbing(Exception): """An operation was tried while we were not climbing"""
class TooLong(Exception): """The rope was too long"""

G = Vec2d(0.0, 980.0)

# Groups for physics
G_CONNECTORS = 1
G_ROPES = 2
G_SURFACES = 3

L_NO_COLLIDE = 1
L_COLLIDE = 2

class Rope(serge.actor.CompositeActor):
    """Represents a rope"""
    
    damping_factor = 10
    rope_group = G_ROPES
    
    def __init__(self, tag, name, link_length, num_links, anchor_size=10, anchor_colour=(255, 0, 0), draw_rope=False,
                    rope_width=2, rope_colour=(0, 0, 0)):
        """Initialise the rope"""
        super(Rope, self).__init__(tag, name)
        #
        self.link_length = link_length
        self.num_links = num_links
        self.anchor_size = anchor_size
        self.anchor_colour = anchor_colour
        self.draw_rope = draw_rope
        self.rope_width = rope_width
        self.rope_colour = rope_colour
        self.quiescent_velocity = GG('rope-quiescent-velocity')
        self.can_go_quiescent = True
        self.is_sleeping = False
        
    def addedToWorld(self, world):
        """Added rope to the world"""
        super(Rope, self).addedToWorld(world)
        #
        # Create the anchor
        self.world = world
        a = serge.actor.Actor('anchor')
        a.setPhysical(serge.physical.PhysicalConditions(mass=10.0, radius=10.0, fixed=True, group=G_ROPES, layers=L_NO_COLLIDE))
        a.visual = serge.blocks.visualblocks.Circle(self.anchor_size, self.anchor_colour)
        a.moveTo(self.x, self.y)
        a.setLayerName(self.getLayerName())
        self.addChild(a)
        #
        # Now each link
        previous = a
        #
        for link in range(self.num_links):
            #
            # Create a link
            l = Climbable('rope-link', '%s-l-%d' % (self.name, link), draw_next=self.draw_rope, draw_colour=self.rope_colour,
                draw_width=self.rope_width)
            l.link_id = link
            l.visual = serge.blocks.visualblocks.Circle(1, (0, 255, 0))
            l.setPhysical(serge.physical.PhysicalConditions(mass=1.0, force=G*1.0, visual_size=True, group=self.rope_group, layers=L_COLLIDE))
            l.moveTo(self.x, self.y+(link+1)*self.link_length)
            l.setLayerName(self.getLayerName())
            l.parent = self
            self.addChild(l)
            #
            # Link to previous
            j = pymunk.SlideJoint(previous.getPhysical().body, l.getPhysical().body, (0,0), (0,0), 0, self.link_length)
            try:
                l.getPhysical().space.add(j)
            except:
                import pdb; pdb.set_trace()
            l.joint = j
            #
            if previous != a:
                l.up_to = previous
                previous.down_to = l
            previous = l
        
    def updateActor(self, interval, world):
        """Update the rope"""
        super(Rope, self).updateActor(interval, world)
        #
        # Dampen motion of the rope links
        velocity_sum = 0
        for link in self.getChildren():
            v = link.getPhysical().body.velocity.length
            velocity_sum += v
            link.getPhysical().body.apply_impulse(-math.exp(-v/self.damping_factor)*link.getPhysical().body.velocity)        
        #
        # Check if the rope is idle - we can use this to turn off the physics calculation
        # and improve framerates
        if not self.is_sleeping and self.can_go_quiescent and 0 < velocity_sum < self.quiescent_velocity:
            self.log.debug('Rope %s has become idle' % self.getNiceName())
            self.goToSleep()
            
    def goToSleep(self):
        """Sleep our physics"""
        self.is_sleeping = True
        #
        # Remove all the physics elements from the simulation
        for link in self.getChildren().findActorsByTag('rope-link'):
            link.getPhysical().space.remove(link.getPhysical().body, link.getPhysical().shape, link.joint)
    
    def wakeUp(self):
        """Wake up physics if needed"""
        if not self.is_sleeping:
            return
        #
        # Add all the physics elements to the simulation
        for link in self.getChildren().findActorsByTag('rope-link'):
            for piece in (link.getPhysical().body, link.getPhysical().shape, link.joint):
                try:
                    link.getPhysical().space.add(piece)
                except Exception, err:
                    self.log.debug('Failed to add to space: %s' % err)
        
    @classmethod    
    def addRopeFrom(cls, world, tag, rock_tags, name, start, end, layer_name, link_length, num_links, *args, **kw):
        """Get a rope with one end at the start and that goes through the end"""
        start_pos = Vec2d(start)
        end_pos = Vec2d(end)
        actual_start_pos = cls._getSafeStartPoint(world, rock_tags, start_pos, end_pos)
        offset = (end_pos - actual_start_pos)
        increment = offset.normalized()*link_length
        #
        # Make sure the rope can go far enough
        links_needed = offset.length / link_length
        if links_needed > num_links:
            raise TooLong('The rope from %s to %s needs %d links, %d is the maximum' % (
                start, end, links_needed, num_links))
        #
        # Create the rope
        rope = cls(tag, name, link_length, num_links, *args, **kw)
        rope.setLayerName(layer_name)
        rope.moveTo(*actual_start_pos)
        world.addActor(rope)
        #
        # Move links to the right place
        last = rope.getChildren()[0]
        for idx, link in enumerate(rope.getChildren()[1:]):
            last_pos = Vec2d(last.x, last.y)
            if idx < links_needed:
                link.moveTo(*(last_pos + increment))
            elif idx >= int(links_needed):
                link.moveTo(*end)
            last = link
        #
        return rope

    @classmethod
    def _getSafeStartPoint(cls, world, rock_tags, start, end):
        """Return the best end point to use for a rope with the given start point
        
        We avoid having the end point be inside another actor
        
        """
        #
        # Find all likely looking bodies we might interact with
        actors = world.getActors().findActorsByTags(rock_tags)
        #
        # Look for hits
        hits = []
        for actor in actors:
            query = actor.getPhysical().shape.segment_query(end, start)
            if query:
                hits.append((query.get_hit_distance(), query.get_hit_point()))
        #
        # Were there any?
        if not hits:
            # None - just use the specified one
            return start
        #
        # Find closest
        hits.sort()
        return hits[0][1]
        
        
class Climbable(serge.actor.Actor):
    """An actor that you can climb up and down"""

    def __init__(self, tag, name, draw_next=False, draw_width=2, draw_colour=(50, 50, 50)):
        """Initialise the Climbable"""
        super(Climbable, self).__init__(tag, name)
        #
        self.up_to = self.down_to = self.parent = None
        self.draw_next = draw_next
        self.draw_width = draw_width
        self.draw_colour = draw_colour
        
    def linkActorTo(self, actor, move=False, link_length=False):
        """Link an actor to ourself"""
        #
        # Move the other actor if needed
        if move:
            actor.moveTo(self.x, self.y)
        #
        # Don't link too close
        length = 0 if not link_length else self.getDistanceFrom(actor)
        j = pymunk.SlideJoint(self.getPhysical().body, actor.getPhysical().body, (0,0), (0,0), 0, 
            max(length, link_length+self.width/2))
        self.getPhysical().space.add(j)
        actor.point_link = j        
        self.log.debug('Linked %s (%s) and %s (%s) with length %s (%s)' % (
            self.getNiceName(), (self.x, self.y), actor, (actor.x, actor.y), link_length+self.width/2,
            self.getDistanceFrom(actor)))
        #
        # Wake up the rope if needed
        if self.parent is not None:
            self.parent.wakeUp()
            
    def renderTo(self, renderer, interval):
        """Render ourself to the given renderer"""
        if self.draw_next and self.down_to and self.layer:  
            layer = renderer.getLayer(self.layer)
            camera = renderer.camera
            if layer.static:
                coords1 = self.getOrigin()
                coords2 = self.down_to.getOrigin()
            elif camera.canSee(self):
                coords1 = camera.getRelativeLocation(self)
                coords2 = camera.getRelativeLocation(self.down_to)
            else: 
                return # Cannot see me
            pygame.draw.line(layer.getSurface(), self.draw_colour, coords1, coords2, self.draw_width)
        else:
            super(Climbable, self).renderTo(renderer, interval)


class Climber(serge.blocks.actors.ScreenActor):
    """An actor that can climb ropes"""
    
    key_l = pygame.K_a
    key_r = pygame.K_d
    key_u = pygame.K_w
    key_d = pygame.K_s
    key_grab = pygame.K_q
    key_switch = pygame.K_e
    
    max_deceleration = 40
    damping_factor = 100000
    auto_disconnect = False
    
    def __init__(self, tag, name, maximum_reach=30, surface_tags=('surface',), 
                    jump_impulse=10000, walk_impulse=500, can_scramble=True):
        """Initialise the climber"""
        super(Climber, self).__init__(tag, name)
        #
        self.maximum_reach = maximum_reach
        self.surface_tags = surface_tags
        self.jump_impulse = jump_impulse
        self.walk_impulse = walk_impulse
        self.can_scramble = can_scramble
        #
        self.obj = None
        self.at_link = None  
        self.grabbed = False 
        self.last_velocity = None 
        self._walking = False
        self._jumping = False
        self._last_jumped = time.time()
        self._jump_recovery = 0.2
        self.acceleration = 0.0
                
    def grabNearestHangPoint(self, tags, move=False, avoid_parent=False, link_length=False):
        """Grab a nearby point - return True if we succeed of False if we fail"""
        #
        # Find the closest link
        objects = self.world.getActors().findActorsByTags(tags)
        distances = []
        for obj in objects:
            if obj != self.obj:
                if self.obj is None or not avoid_parent or self.obj.parent != obj.parent:
                    #
                    # Correct the distance to account for the size of the object and ourself 
                    # because what is important is the gap between the edges
                    distances.append((obj.getDistanceFrom(self)-self.width/2, obj))
        distances.sort()
        #
        # Check we are close enough
        if not distances or distances[0][0] > self.maximum_reach:
            self.log.debug('Too far to grab %s (%s)' % (tags, distances[0][0] if distances else 'none found'))
            return False
        #
        # Let go if we need to
        if self.obj:
            self.letGoOfHangPoint()
        #
        # Link to the point
        obj = distances[0][1]
        obj.linkActorTo(self, link_length=link_length, move=move)
        self.obj = obj
        if self.obj.parent:
            self.obj.parent.can_go_quiescent = False
        #
        self.log.debug('Grabbed onto %s' % obj.getNiceName())
        #
        return True
        
    def letGoOfHangPoint(self):
        """Let go of the point"""
        if not self.obj:
            raise NotClimbing('Tried to let go of the rope but was not climbing')
        self.getPhysical().space.remove(self.point_link)
        if self.obj.parent:
            self.obj.parent.can_go_quiescent = True
        self.obj = self.grabbed = None

    def moveUp(self):
        """Move up"""
        self.moveVertically(self.obj.up_to, self.jump_impulse)
    
    def moveDown(self):
        """Move down"""
        self.moveVertically(self.obj.down_to, 0)
        
    def moveVertically(self, new_object, thrust):
        """Try to move to a new object"""
        if not self.obj:
            raise NotClimbing('Tried to move down but was not climbing')
        #
        if new_object:
            #
            # Remove the old joint
            self.letGoOfHangPoint()
            new_object.linkActorTo(self, link_length=False)
            self.obj = new_object
            if self.obj.parent:
                self.obj.parent.can_go_quiescent = False
        elif self.auto_disconnect:
            self.letGoOfHangPoint()
            self.getPhysical().body.apply_impulse((0, -self.jump_impulse))
        
    def updateActor(self, interval, world):
        """Update the climber"""
        super(Climber, self).updateActor(interval, world)
        #
        body, keyboard, connected = self.getPhysical().body, self.keyboard, self.obj != None
        #
        # Check decceleration (damage)
        if self.last_velocity is not None:
            self.acceleration = ((body.velocity - self.last_velocity)/interval).length
            if abs(self.acceleration) > self.max_deceleration:
                self.log.debug('High acceleration (%s)' % self.acceleration)
                
        self.last_velocity = Vec2d(body.velocity)
        self._walking = False
        self._jumping = False
        #
        # Motion of the climber when attached to a rope
        if connected:
            if keyboard.isClicked(self.key_l):
                self.log.debug('Kick left')
                body.apply_impulse((-10000, 0))
            if keyboard.isClicked(self.key_r):
                self.log.debug('Kick right')
                body.apply_impulse((+10000, 0))
            if keyboard.isClicked(self.key_u):
                self.log.debug('Move up')
                self.moveUp()
            if keyboard.isClicked(self.key_d):
                self.log.debug('Move down')
                self.moveDown()
            if self.keyboard.isClicked(self.key_grab):
                if self.grabbed:
                    self.grabbed = False
                else:
                    self.log.debug('Let go')
                    self.letGoOfHangPoint()
            if self.keyboard.isDown(self.key_switch):
                if not self.grabbed:
                    if not self.can_scramble or not self.grabNearestHangPoint(self.surface_tags, link_length=True):
                        if self.grabNearestHangPoint(['rope-link'], avoid_parent=True, link_length=False):
                            self.grabbed = True
                    else:
                        self.grabbed = True
            if self.keyboard.isClicked(self.key_switch):
                self.grabbed = False
        else:
            #
            # Motion when not attached to the rope
            if keyboard.isDown(self.key_l):
                # Walk left
                body.apply_impulse((-self.walk_impulse, 0))
                self._walking = True
            if keyboard.isDown(self.key_r):
                # Walk right
                body.apply_impulse((+self.walk_impulse, 0))
                self._walking = True
            if keyboard.isDown(self.key_u):
                if self.isOnSurface() and time.time() - self._last_jumped > self._jump_recovery:
                    self.log.debug('Jump')
                    self.getPhysical().body.apply_impulse((0, -self.jump_impulse))
                    self._jumping = True
                    self._last_jumped = time.time()
                else:
                    self.log.debug('Not on a surface')
            if keyboard.isDown(self.key_grab):
                if not self.can_scramble or not self.grabNearestHangPoint(self.surface_tags, link_length=True):
                    if self.grabNearestHangPoint(['rope-link'], avoid_parent=True, link_length=False):
                        self.grabbed = True
                else:
                    self.grabbed = True
            #
            # Damping
#            if self.isOnSurface():
#                v = self.getPhysical().body.velocity.length
#                self.getPhysical().body.apply_impulse(-math.exp(-v/self.damping_factor)*self.getPhysical().body.velocity)        

    def isOnSurface(self, delta=5):
        """Return True if the actor is on a surface"""
        test_point = serge.geometry.Point(self.x, self.y+self.height/2+delta)
        for actor in self.world.getActors().findActorsByTags(self.surface_tags):
            if test_point.isInside(actor):
                return actor
        else:
            return False

    def isHanging(self):
        """Return True if we are hanging"""
        return self.obj is not None
                    
    def isWalking(self):
        """Return True if we are walking"""
        return self._walking and self.isOnSurface()
    
    def isJumping(self):
        """Return True if we are jumping"""
        return self._jumping
        
    def getRope(self):
        """Return the current rope"""
        return self.obj.parent
