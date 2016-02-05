#!/usr/bin/env python
#coding=utf-8
import pygame
from isospace import IsoGrid
import gamebase
import utils

def test():
    game = gamebase.GameBase((400,400),30)
    game.start_scale(2)
    count = 0
    tile_img = utils.load_image("iso_cursor_01.png")
    tiles = pygame.sprite.Group()
    ig = IsoGrid((10,5),(100,0))
    r = pygame.Rect((0,0),(18,10))
    for x in range(10):
        for y in range(10):
            s = pygame.sprite.Sprite(tiles)
            s.image = tile_img
            s.rect = tile_img.get_rect()
            s.rect.bottomleft = ig.get_bl((x,y))
    while True:
        game.clock.tick(30)
        events = game.get_events()
        iso_pos = ig.get_iso(game.get_mousepos())
        
        tiles.draw(game.screen)
        r.bottomright = ig.get_br(iso_pos)
        pygame.draw.rect(game.screen,(0,0,0),r,1)
        game.flip()
        game.screen.fill((120,120,120))
        pygame.display.set_caption(str(iso_pos) + str(game.get_mousepos()))
        count += 1

test()