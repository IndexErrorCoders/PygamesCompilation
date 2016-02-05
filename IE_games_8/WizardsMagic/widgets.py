#!/usr/bin/env python
#Wizards Magic
#Copyright (C) 2011-2014  https://code.google.com/p/wizards-magic/
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# vim: set fileencoding=utf-8 :
try: 
    import pygame
    from pygame.locals import *
    from pygame import Surface, draw
    yes_pygame = True
except ImportError:
    yes_pygame = False
import globals

class TxtInput(pygame.sprite.Sprite):
    ''' class handling input box:
    pos: # of line from the top of form
    label: box label
    text: text inside box
    length: box length in chars
    numeric: True=accept only numbers
    enabled: false=disabled box
    key: configuration key
    '''
    def __init__(self, pos=0, label="", text="", length=0, numeric=False, enabled=True, key=""):
        pygame.sprite.Sprite.__init__(self)
        self.type = 'txtinput'
        self.color = (255,255,255)
        self.color_disable = (95,245,244)
        self.font = pygame.font.Font(globals.current_folder + "/misc/DroidSans.ttf", 18)
        self.pos = pos
        self.label = label
        self.text = text[:length]
        self.length = length
        self.key = key
        self.size = self.font.size("O" * (self.length+1))[0]
        self.focus = False
        self.currpos = len(self.text)
        self.numeric = numeric
        self.enabled = enabled
        self.label_image = self.font.render(self.label,True,self.color)
        if self.enabled:
            self.text_image = self.font.render(self.text,True,self.color)
        else:
            self.text_image = self.font.render(self.text,True,(self.color_disable))
        self.label_rect = self.label_image.get_rect()
        self.text_rect = self.text_image.get_rect()
        self.image = None
        self.rect = None
        globals.menu_group.add(self)

    def draw(self):

        bgrect = globals.background.get_rect()
        menupos = globals.menu_bg.get_rect()
        menupos.centery = globals.background.get_rect().centery

        self.label_rect.left = bgrect.centerx - self.label_rect.width - 7  #label X coord (left side from center)
        self.label_rect.top = menupos.top + 50 + (self.label_rect.height + 5) * self.pos

        self.text_rect.left = bgrect.centerx + 7 # text X coord (right size from center)
        self.text_rect.top = self.label_rect.top

        self.image = pygame.Surface((self.label_rect.width + 14 + self.size, self.font.get_linesize()), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.left = self.label_rect.left
        self.rect.top = self.label_rect.top
        self.image.blit(self.label_image, (0,0))
        self.image.blit(self.text_image, (self.label_rect.width + 14,0))

        if self.focus:
            #X coordinate of the cursor
            cursorx = self.font.size(self.text[:self.currpos])[0]
            cursorx += self.label_rect.width + 14
            draw.line(self.image, (255,255,255), (cursorx ,0),(cursorx , self.font.get_height()))

        globals.background.blit(self.image, self.label_rect)
    def update(self):
        self.draw()
    def enable(self):
        self.enable=True
        self.text_image = self.font.render(self.text,True,self.color)
    def disable(self):
        self.enable=False
        self.text_image = self.font.render(self.text,True,self.color_disable)
    def change(self, event):

        if self.currpos > len(self.text):
            self.currpos = len(self.text)

        if self.enabled:
            if event.type == pygame.KEYUP:
                if event.key==K_RETURN:
                    self.focus=False
                    globals.itemfocus=None
                if event.key == pygame.K_BACKSPACE:
                    if self.currpos == 0:
                        return
                    self.text = self.text[:self.currpos-1] + self.text[self.currpos:]
                    self.currpos -= 1
                    if self.currpos < 0:
                        self.currpos = 0
                elif event.key == pygame.K_DELETE:
                    self.text = self.text[:self.currpos] + self.text[self.currpos+1:]
                elif event.key == pygame.K_LEFT:
                    self.currpos -= 1
                    if self.currpos < 0:
                        self.currpos = 0
                elif event.key == pygame.K_RIGHT:
                    self.currpos += 1
                    if self.currpos > len(self.text):
                        self.currpos = len(self.text)
                elif event.key == pygame.K_HOME:
                    self.currpos = 0
                elif event.key == pygame.K_END:
                    self.currpos = len(self.text)
                elif event.key in (pygame.K_RSHIFT, pygame.K_LSHIFT, pygame.K_RETURN, pygame.K_TAB):
                    pass
                else:
                    if len(self.text)<self.length:
                        self.text = self.text[:self.currpos] + pygame.key.name(event.key) + self.text[self.currpos:]
                        self.currpos += 1

                if self.enabled:
                    self.text_image = self.font.render(self.text,True,self.color)
                else:
                    self.text_image = self.font.render(self.text,True,(self.color_disable))
                self.draw()
    def onmousedown(self):
        if self.enabled:
            if globals.itemfocus:
                globals.itemfocus.focus = False
            self.focus = True
            globals.itemfocus = self
    def onmouseup(self):
        pass

class CheckBox(pygame.sprite.Sprite):
    ''' class handling checkbox:
    pos: # of line from the top of form
    label: CheckBox label
    value: True/False
    enabled: false=disabled box
    key: configuration key
    '''
    def __init__(self, pos=0, label="", value=False, enabled=True, key=""):
        pygame.sprite.Sprite.__init__(self)
        self.type = 'checkbox'
        self.color = (255,255,255)
        self.color_disable = (95,245,244)
        self.font = pygame.font.Font(globals.current_folder + "/misc/DroidSans.ttf", 18)
        self.pos = pos
        self.label = label
        self.value = value
        self.key = key
        self.focus = False
        self.enabled = enabled
        if self.enabled:
            self.label_image = self.font.render(self.label,True,self.color)
        else:
            self.label_image = self.font.render(self.label,True,(self.color_disable))
        self.label_rect = self.label_image.get_rect()
        self.value_on = pygame.image.load(globals.current_folder + '/misc/checkbox_on.gif').convert()
        self.value_off = pygame.image.load(globals.current_folder + '/misc/checkbox_off.gif').convert()
        if value:
            self.value_image = self.value_on
        else:
            self.value_image = self.value_off

        self.image = None
        self.rect = None
        globals.menu_group.add(self)

    def draw(self):

        bgrect = globals.background.get_rect()
        menupos = globals.menu_bg.get_rect()
        menupos.centery = globals.background.get_rect().centery

        self.label_rect.left = bgrect.centerx - self.label_rect.width - 7  #label X coord (left side from center)
        self.label_rect.top = menupos.top + 50 + (self.label_rect.height + 5) * self.pos

        self.image = pygame.Surface((self.label_rect.width + 14 + self.value_image.get_rect().width, self.font.get_linesize()), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.left = self.label_rect.left
        self.rect.top = self.label_rect.top
        self.image.blit(self.label_image, (0,0))
        self.image.blit(self.value_image, (self.label_rect.width + 14,0))

        globals.background.blit(self.image, self.label_rect)
    def update(self):
        self.draw()
    def enable(self):
        self.enable = True
        self.label_image = self.font.render(self.label,True,self.color)
    def disable(self):
        self.enable = False
        self.label_image = self.font.render(self.label,True,(self.color_disable))
    def change(self): #Hot Fix
        return 0
    def onmousedown(self):
        if self.enabled:
            if globals.itemfocus:
                globals.itemfocus.focus = False
            self.focus = True
            globals.itemfocus = self
        if self.value:
            self.value_image = self.value_off
            self.value = False
        else:
            self.value_image = self.value_on
            self.value = True
    def onmouseup(self):
        pass
    def onmouseout(self):
        pass
    def onmouse(self):
        pass

def main():

    pygame.init()
    globals.screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Wizards Magic')
    globals.background = pygame.Surface(globals.screen.get_size())
    globals.background = globals.background.convert()
    globals.background.fill((250, 250, 250))

    ti = TxtInput(0,"SOUND","192.168.111.255","",5)
    globals.background = pygame.image.load(globals.current_folder + '/misc/menu_bg.jpg').convert_alpha()
    globals.menu_bg = pygame.image.load(globals.current_folder + '/misc/menu_selections_bg.jpg').convert_alpha()
    menupos = globals.menu_bg.get_rect()
    menupos.centerx = globals.background.get_rect().centerx -2 # '-2' hack due lazy designer :)
    menupos.centery = globals.background.get_rect().centery -1 # '-1' hack due lazy designer :)
    globals.background.blit(globals.menu_bg, menupos)
    globals.screen.blit(globals.background, (0, 0))
    pygame.display.flip()

    while 1:
        globals.menu_group.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                return

            print event
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    print "qqqqqqqqqqqqqqqqqq"
                else:
                    print event.key
                    print pygame.key.name(event.key)
        globals.screen.blit(globals.background, (0, 0))
        pygame.display.flip()
        pygame.time.wait(200)
if __name__ == '__main__': main()
