#####################################################################
# Auxiliary functions for sprite handling

import GameData
import pygame
import os.path
from pygame.locals import *
from Source import Tank, RespawnPoint

#see if we can load more than standard BMP
if not pygame.image.get_extended():
    raise SystemExit, "Sorry, extended image module required"


def load_image(file, colorkey=-1):
    """loads an image, prepares it for play
    colourkey = -1 forces the left-top pixel colour to be transparent,
    use colourkey = None for non transparant surfaces """
    file = os.path.join('Sprites', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit, 'Could not load image "%s" %s'%(file, pygame.get_error())
    surface = surface.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = surface.get_at((0,0))
        surface.set_colorkey(colorkey, RLEACCEL)
    return surface

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs

def load_background(file, colorkey=-1):
    """loads an image, prepares it for play
    colourkey = -1 forces the left-top pixel colour to be transparent,
    use colourkey = None for non transparant surfaces """
    file = os.path.join('Backgrounds', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit, 'Could not load image "%s" %s'%(file, pygame.get_error())
    surface = surface.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = surface.get_at((0,0))
        surface.set_colorkey(colorkey, RLEACCEL)
    return surface

def load_backgrounds(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs

def draw_background(background, bgdtile, screen, blacksquare = False):
    for x in range(0, GameData.screenrect.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    if GameData.battleground[GameData.battlegroundnr].draw_water:
        for pool in GameData.battleground[GameData.battlegroundnr].water:
            pygame.draw.rect(background, (33,33,200), pool, 0)        
    if GameData.battleground[GameData.battlegroundnr].draw_walls:
        for wall in GameData.battleground[GameData.battlegroundnr].walls:
            pygame.draw.rect(background, (33,33,33), wall, 0)
    if blacksquare:
        pygame.draw.rect(background, (0,0,0), (60,101,681,477), 0)
    screen.blit(background, (0,0))
    pygame.display.flip()

def determine_visibility(respawn_points, tanks, tanklist, active_screen, move_tanks_to_respawn_point = False):
    for respawn_point in respawn_points:
        respawn_point.kill()
    count = 0
    for respawn_point in GameData.battleground[GameData.battlegroundnr].respawnpoints:
        RespawnPoint(respawn_point[0],respawn_point[1],respawn_point[2])
        if move_tanks_to_respawn_point:
            tanklist[count].move_to_respawn_point(count)
        tanklist[count].visible = True
        count += 1
        for respawn_point in pygame.sprite.spritecollide(active_screen, respawn_points, 0):
            respawn_point.visible = False
        for tank in pygame.sprite.spritecollide(active_screen, tanks, 0):
            tank.visible = False 
