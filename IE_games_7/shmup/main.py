#!/usr/bin/env python
#coding=utf-8
# Shmup & build

import os
import math
from random import randint as rnd


from pygame.locals import *

from nested2d import Nested2d
from nested2d import nested2d_fromstring
import isospace
import utils
import images
from images import make_buildingset
import shapes
import pathfinding as ptf
import global_access as ga
import gui

from vectorfunc import *
from buildings import *
from constants import *
from shmupobjects import *
from roadlib import *

BUILD_HOTKEYS = {
K_r: Road,
K_b: Barrack,
K_a: Barrier,
K_s: Barrier2,
K_g: PowerGen,
K_c: CommandCenter,
K_DELETE: Destroy,
K_n: Cannon
}

class Station(object):
    def __init__(self):
        self.free_tiles = None
        self.loaded_build = None
        self.economy = 0
        self.roadhints = pygame.sprite.Group()
        self.roadpath = []
        self.drag = False
        
    def make_maps(self, form):
        self.free_tiles = form
        self.buildings = Nested2d(self.free_tiles.x_len, self.free_tiles.y_len)
        
    def check_free(self, *indexes):
        for (x,y) in indexes:
            if 0 <= x < self.free_tiles.x_len and 0 <= y < self.free_tiles.y_len:
                if isinstance(self.buildings[x][y],Road):
                    return False
                elif self.free_tiles[x][y]:
                    continue
                else:
                    return False
            else:
                return False
        return True
    
    def load_build(self,bc):
        self.loaded_build = bc
        
    def unload_build(self):
        self.loaded_build = None
        if self.drag:
            self.drag = False
            for s in self.roadhints.sprites():
                s.kill()
    
    def build(self):
        if self.loaded_build is Road:
            self.drag = True
            self.road_end = self.road_start = ga.stationGrid.get_iso(get_mousepos())
            self.roadpath = ptf.pathfind(self.free_tiles, self.road_start, self.road_end)
            
        elif self.loaded_build is Destroy:
            x,y = ga.station_iso
            building = self.buildings[x][y]
            if building and 0 <= x < ga.station.free_tiles.x_len and 0 <= y < ga.station.free_tiles.y_len:
                building.destroy()
                
        elif self.loaded_build is not None:
            anchor = ga.stationGrid.get_iso(get_mousepos())
            x,y = self.loaded_build.anchor
            pos = anchor[0] - x, anchor[1] - y
            size = self.loaded_build.size
            if self.loaded_build.check_free[0](pos, self.loaded_build):
                print self.loaded_build
                self.loaded_build(anchor)
                    
    def road_drag(self,  drag):
        if self.drag and drag:
            if self.road_end != ga.station_iso:
                self.road_end = ga.station_iso
                self.roadpath = ptf.pathfind(self.free_tiles, self.road_start, self.road_end)
                self.make_roadhints()
                
        elif self.drag :
            print self.roadpath
            self.drag = False
            for x,y in self.roadpath:
                if not isinstance(self.buildings[x][y],Road):
                    Road((x,y))
            for s in self.roadhints:
                s.kill()

            
                
    def make_roadhints(self):
        for s in self.roadhints:
            s.kill()
        for i in self.roadpath:
            p = ga.stationGrid.get_bl(i)
            s = BuildingPiece(Road.hint,p)
            self.roadhints.add(s)
            
class LineManager(object):
    def __init__(self):
        self.lines = []
        self.colors = []
        self.do_draw = True
    def reg(self, i, color):
        self.lines.append(i)
        self.colors.append(color)

    def draw(self, surface):
        if self.do_draw:
            for n in range(len(self.lines)):
                i = self.lines.pop()
                pygame.draw.line(surface,self.colors[n], i[0],i[1])
                
    def toggle(self):
        self.do_draw = not self.do_draw
        
class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = images.cursor01
        self.rect = self.image.get_rect()
    def update(self):
        self.rect.topleft = get_mousepos()

class IsoCursor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.defaultimage = images.isocursor01
        self.image = self.defaultimage
        self.rect = self.image.get_rect()
        self.offset = 0,TH
        self.loaded_cls = None
        
    def update(self):
        if self.loaded_cls is not None:
            pos = ga.station_iso
            x,y = self.loaded_cls.anchor
            pos = pos[0] -x, pos[1] -y
            size = self.loaded_cls.size
            indexes = make_indexes(pos, size)
            if self.loaded_cls.check_free[0](pos,self.loaded_cls):
                self.image = self.loaded_cls.hint
                self.rect = self.image.get_rect()
            else:
                self.image = self.loaded_cls.badhint
                self.rect = self.image.get_rect()
        else:
            self.image = self.defaultimage
            self.rect = self.image.get_rect()
            
        self.rect.bottomleft = itersum(ga.stationGrid.get_tl(ga.station_iso),self.offset)
        
    def load_hint(self,cls):
        self.loaded_cls = cls
        x = (-cls.size[1] - cls.anchor[0] + cls.anchor[1])*TX+TX
        y = ((cls.size[0] - cls.anchor[0]) + (cls.size[1]-cls.anchor[1]))*TY
        self.offset = x,y
        
    def unload_hint(self):
        self.loaded_cls = None
        self.offset = 0,TH

        
def make_indexes((x,y), (xsize,ysize)): # returns a list of indexes from topindex and size
        return [[x+nx, y + ny] for nx in range(xsize) for ny in range(ysize)]
    
    
def get_mousepos():
    x,y = pygame.mouse.get_pos()
    return x/SCALE, y/SCALE



class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, index):
        pygame.sprite.Sprite.__init__(self)
        
        self.rect = pygame.Rect(pos, (20,20))
        self.index = index
        self.image = images.stationFloor01
        self.building = None
        
    def place(self, builing_index):
        
        self.buildning = building_index
        
class Decoration(pygame.sprite.Sprite):
    def __init__(self,pos, image, groups):
        pygame.sprite.Sprite.__init__(self, groups)
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.topleft = pos
class DistantStar(pygame.sprite.Sprite):
    def mk_img(color):
        i = pygame.Surface((1,1))
        i.fill(color)
        return i

    dir = normalize((2,1))
    images = [mk_img(c) for c in ((100,50,50),(150,150,150),(100,100,100))]
    count = 0
    max = 40
    def __init__(self, pos, speed):
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.image = random.choice(self.images)
        self.floatpos = float(pos[0]),float(pos[1])
        self.rect = pygame.Rect(pos, (2,2))
        self.move = get_mul(self.dir, speed)
        DistantStar.count +=1
        
    def update(self):
        self.floatpos = get_add(self.floatpos, self.move)
        self.rect.topleft = self.floatpos
        if self.rect.left > SCREENSIZE[0] or self.rect.top > SCREENSIZE[1]:
            self.kill()
            DistantStar.count -=1

def spawn_star():
    if not random.randint(0,8) and DistantStar.count < DistantStar.max:
        if random.randint(0,1):
            DistantStar((random.randint(0,300),0),(random.random()+0.02)*2)
        else:
            DistantStar((0,random.randint(0,200)),random.random()+0.02)
    
    if not random.randint(0,14) and DistantStar.count < DistantStar.max:
        if random.randint(0,1):
            DistantStar((random.randint(0,300),0),(random.random()+0.02)*10)
        else:
            DistantStar((0,random.randint(0,200)),(random.random()+0.02)*10)
    
class GridSquare(Tile):
    def __init__(self, pos, index):
        Tile.__init__(self, pos, index)
        self.image = images.gridSquare
        
def main():
    # Initiating, screen, clock etc.
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.display.init()
    pygame.display.set_caption("shmup & build")
    
    surf = pygame.Surface((32,32),SRCALPHA)
    icon = pygame.image.load(os.path.join("data","python_icon.png"))
    icon.set_colorkey((0,0,0))
    surf.blit(icon,(0,0))
    pygame.display.set_icon(surf)
    screen = pygame.display.set_mode(WINDOWSIZE, DOUBLEBUF|HWSURFACE)
    presurf = pygame.Surface(SCREENSIZE,HWSURFACE)
    clock = pygame.time.Clock()
    ga.count = 0
    quitflag = False
    ga.lm = LineManager()
    aManager = AttackerManager()
    aManager.reg_unit(15,LaserDrone,((10,10),))
    aManager.reg_unit(30,LaserDrone,((10,18),))
    aManager.reg_unit(52,LaserDrone,((11,2),))
    aManager.reg_unit(66,LaserDrone,((5,16),))
    for i in range(20):
        aManager.reg_unit(rnd(20,1000),LaserDrone,((rnd(0,12),rnd(0,25)),))
    
    #---- LOADING GRAPHICS ----
    # gui
    images.button01 = utils.load_image("button_01.png")
    
    # cursors
    images.isocursor01 = utils.load_image("iso_cursor_01.png")
    images.cursor01 = utils.load_image("cursor_01.png")
    
    # shmup images
    images.player_ship = utils.load_image("ship_04.png")
    images.ship_02 = utils.load_image("ship_08.png")
    images.ship_05 = utils.load_image("ship_05.png")
    images.ship_06 = utils.load_image("ship_07.png")
    
    # projectiles
    images.beam01 = utils.load_image("beam_01.png")
    img = utils.load_image("beam_01_end.png")
    images.beam01_end = images.cut_sheet(img, (12,6))
    img = utils.load_image("beam_02.png")
    images.beam02 = images.cut_sheet(img, (8,6))
    
    # explotions
    img = utils.load_image("explosion_01.png")
    images.explosion_01 = images.cut_sheet(img,(26,26))
    
    
    # floor tiles
    images.stationFloor01 = utils.load_image("station_floor_01.png")
    images.stationDec01 = utils.load_image("station_decoration_03.png")
    images.gridSquare = utils.load_image("iso_square_1.png")
    
    # buildings
    make_buildingset("building03",  (2,2), "building_03.png", PowerGen)
    make_buildingset("building04",  (2,2), "building_04.png", Barrack)
    make_buildingset("building06",  (1,1), "building_06.png", Barrier)
    make_buildingset("building07",  (2,1), "building_08.png", Barrier2)
    make_buildingset("road", (1,1), "road_01.png", Road)
    make_buildingset("comcenter01",(3,3),"building_05.png", CommandCenter)
    make_buildingset("cannon01", (2,1), "cannon_01.png",Cannon)
    
    # walkers
    images.repairdrone_01 = images.cut_sheet(utils.load_image("robot_01.png"),
    (11,15))
    
    images.square02 = utils.load_image("iso_square_2.png")
    images.square03 = utils.load_image("iso_square_3.png")
    
    #--------
    
    #sprite groups
    generic = pygame.sprite.Group()
    ga.generic = generic
    cursors = pygame.sprite.OrderedUpdates()
    guiGroup = pygame.sprite.Group()
    bottomDec = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    topDec = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    shmupObjects = ga.shmupObjects = pygame.sprite.LayeredUpdates()
    ga.stationGridGround = pygame.sprite.OrderedUpdates()
    buildings = pygame.sprite.LayeredUpdates()
    ndBuildings = pygame.sprite.Group() # non drawing part of building
    
    #tying sprite classes to groups
    IsoCursor.groups = (cursors,)
    Cursor.groups = (cursors,)
    BuildingPiece.groups = (buildings,)
    DistantStar.groups = (stars,)
    Explosion.groups = (generic,)
    DyingAnim.groups = (generic,)
    for cls in Projectile.__subclasses__():
        cls.groups = (projectiles,)
    for cls in Building.__subclasses__():
        cls.groups = (ndBuildings,)
    for cls in Walker.__subclasses__():
        cls.groups = (generic,)
    for cls in ShmupObject.__subclasses__():
        cls.groups = (shmupObjects,)
    for cls in gui.Button.__subclasses__():
        cls.groups = (guiGroup,)
    
    
    #isoSpaces
    ga.shmupGrid = isospace.IsoGrid((TX, TY), (250,20))
    ga.stationGrid = isospace.IsoGrid((TX, TY), ga.shmupGrid.get_mt((22,0)))
    
    #player
    playership_start = ga.shmupGrid.get_tl((PS_ROW,18))
    playerShip = PlayerShip(playership_start,(10,10))
    
    #decorations
    stationDec = Decoration(
    (ga.stationGrid.get_left((0,24))-1,  ga.stationGrid.get_top((0,0))),
    images.stationDec01, bottomDec)
    
    # gui components
    barrackButton = gui.BuildingButton((40,220),(4,2), Barrack, images.building04)
    cannonButton = gui.BuildingButton((90,250),(4,4), Cannon, images.cannon01)
    roadButton = gui.BuildingButton((40,250), (10,10), Road, images.road)
    roadButton.add_img(images.road, (10+ TX,10-TY))
    PowerGenButton = gui.BuildingButton((40,280),(4,-2), PowerGen, images.building03)
    Barrier2Button = gui.BuildingButton((90,280),(8,2), Barrier2, images.building07)
    
    #cursors
    isoCursor =ga.isoCursor = IsoCursor()
    cursor = ga.cursor = Cursor()
    
    #Station
    stationform = nested2d_fromstring(shapes.station, {"#":1, " ":0})
    station = ga.station = Station()
    station.floor = Nested2d(stationform.x_len,stationform.y_len)
    station.make_maps(nested2d_fromstring(shapes.station, {"#":True, " ":False}))
    
    #pathfinding
    ga.ptfstart = None

    for i in stationform.loop_all():
        i,x,y = i
        if i:
            station.floor[x][y] = Tile(ga.stationGrid.get_tl((x,y)),(x,y))
            station.floor[x][y].add(ga.stationGridGround)
            
    for x in range(-10,SHMUPGRID_X):
        for y in range(SHMUPGRID_Y):
            GridSquare(ga.shmupGrid.get_tl((x,y)),(x,y)).add(ga.stationGridGround)

    
    for i in range(600):
        spawn_star()
        stars.update()
    ## -------- MAIN LOOP --------  
    while not quitflag:
        clock.tick(60)
        ga.count += 1
        ga.station_iso = ga.stationGrid.get_iso(get_mousepos())
        ga.shmup_iso = ga.shmupGrid.get_iso(get_mousepos())
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                quitflag = True
                
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    quitflag = True
                elif event.key == K_TAB:
                    ga.lm.toggle()
                building_cls = BUILD_HOTKEYS.get(event.key)
                if building_cls:
                    station.load_build(building_cls)
                    isoCursor.load_hint(building_cls)
                    
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if ga.shmupGrid.get_iso(get_mousepos())[0] < 22:
                        #playerShip.fire()
                        pass
                    station.build()
                    guiGroup.update(get_mousepos())
                    
                if event.button == 3:
                    isoCursor.unload_hint()
                    station.unload_build()
                    
                    
        # check keys and buttons held down
        if pygame.mouse.get_pressed()[0]:
            station.road_drag(True)
            playerShip.is_firing = True
        else:
            station.road_drag(False)
            playerShip.is_firing = False
        # correct mouse pos
        mx, my = get_mousepos()
        ga.iso_pos_station = ga.stationGrid.get_iso((mx, my))
        ga.iso_pos_space = ga.stationGrid.get_iso((mx, my))
        
        aManager.update(ga.count)
        
        spawn_star()
        generic.update()
        cursors.update()
        stars.update()
        projectiles.update()
        buildings.update()
        ndBuildings.update()
        shmupObjects.update()
        
        ip = ga.stationGrid.get_iso((mx,my))
        
        presurf.fill((0,0,8))
        
        stars.draw(presurf)
        bottomDec.draw(presurf)
        ga.stationGridGround.draw(presurf)
        projectiles.draw(presurf)
        shmupObjects.draw(presurf)
        buildings.draw(presurf)
        generic.draw(presurf)
        
        
        pygame.draw.polygon(presurf,(130,140,140),((0,326-155),(310,326),(0,326)))
        pygame.draw.polygon(presurf,(100,100,100),((0,326-150),(300,326),(0,326)))        
        guiGroup.draw(presurf)
        
        if pygame.mouse.get_focused():
            cursors.draw(presurf)
        
        pos = ga.stationGrid.get_iso(get_mousepos())
        if pos:
            if 0 <= pos[0] < STATIONGRID_X and 0 <= pos[1] < STATIONGRID_Y:
                pos = ga.stationGrid.get_tl(pos)
                
                
        ga.lm.draw(presurf)
        #pygame.draw.rect(presurf, (0,0,0), ga.stationGrid.get_rect(), 1)
        pygame.transform.scale(presurf, WINDOWSIZE, screen)
        pygame.display.flip()
        
        # print info in window caption
        pygame.display.set_caption("fps" + str(int(clock.get_fps())) + str(ga.station_iso) + str(get_mousepos()))
        

if __name__ == "__main__":
    main()