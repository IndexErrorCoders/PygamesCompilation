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
    yes_pygame = True
except ImportError:
    yes_pygame = False
import sys
import os
import time
import socket
import sockets
import WizardsMagicServer
import globals
import options
current_folder = os.path.dirname(os.path.abspath(__file__))
#t = gettext.translation('interface', current_folder+'/languages', languages=['ru'])
#_ = t.ugettext
#t.install()

class MenuButton(pygame.sprite.Sprite):
    ''' menu item '''
    def __init__(self, pos=0, text="", cmd="", enabled=True, loc=(0,0)):
        ''' Element of menu. Parameters:
            pos=position of item inside menu
            text=text to display
            cmd=function to ejecute when click on item
            enabled=True/False to enable/disable item
            loc=(X,Y) coordinates (to use this, put pos=-1) relative to 0,0 menu_bg
            '''
        pygame.sprite.Sprite.__init__(self)
        self.type = 'button'
        self.color = (255,255,255)
        self.font = pygame.font.Font(current_folder+"/misc/Domestic_Manners.ttf", 20)
        self.text=text
        self.pos=pos
        self.cmd=cmd
        self.enabled=enabled
        self.loc=loc

        self.image_normal = self.font.render(self.text,True,self.color)
        self.image_pressed = self.font.render(self.text,True,(176,154,133))
        self.image_disabled = self.font.render(self.text,True,(95,245,244))
        if self.enabled:
            self.image = self.image_normal.copy()
        else:
            self.image = self.image_disabled.copy()
        self.rect=self.image.get_rect()
        self.surface_backup = self.image.copy()
        globals.menu_group.add(self)
    def draw(self):
        self.image = self.surface_backup.copy()
        bgrect = globals.background.get_rect()
        menupos = globals.menu_bg.get_rect()
        menupos.centery = globals.background.get_rect().centery
        if self.pos>=0:
            self.rect.centerx = bgrect.centerx
            self.rect.top = menupos.top + 50 + (self.rect.height+5)*self.pos
        else:
            menupos.centerx = globals.background.get_rect().centerx
            self.rect.top = menupos.top + self.loc[1]
            self.rect.left = menupos.left + self.loc[0]
        globals.background.blit(self.image, self.rect)
    def update(self):
        self.draw()
    def onmouse(self):
        if self.enabled:
            self.image = self.image_pressed
            self.surface_backup = self.image.copy()
    def onmouseout(self):
        if self.enabled:
            self.image = self.image_normal
            self.surface_backup = self.image.copy()
    def onmousedown(self):
        if self.enabled:
            exec(self.cmd)
            self.image = self.image_pressed
            self.surface_backup = self.image.copy()
    def onmouseup(self):
        pass
    def default(self):
        self.image = self.image_normal
        self.surface_backup = self.image.copy()

def clean_question():
    globals.question=False
    globals.answer=""
    globals.answer_cmd=""
    globals.gameinformationpanel.show=False

def menu_esc_question():
    globals.gameinformationpanel.display(_("  You are leaving the game. Are you sure? (Y/N)"), persistent=True)
    globals.question=True
    globals.answer=""
    globals.answer_cmd="menu.menu_esc()"
    globals.answer_maxchar=1

def menu_esc():
    ''' function called after the user press ESC key and answer question '''
    if globals.answer.upper()=='Y':
        if globals.stage==0:
            exit_program()
        elif globals.stage<=2:
            globals.stage=0
        if globals.cli:
            if not globals.opponent_disconnect:
                sockets.query({"action":"bye","player_id":globals.player_id})
            else:
                sockets.query({"action":"bbye"})

    clean_question()

def menu_startsinglegame():
    ''' function called after the user click start menu item'''
    globals.stage=1
    globals.cli = False
    globals.ai = True
    globals.gameinformationpanel.show=False
def menu_startserver():
    ''' function called after the user click Start Server item '''
    if not globals.server_thread: 
        globals.server_thread = WizardsMagicServer.Server()
        globals.server_thread.start()
        globals.gameinformationpanel.display("  Server listening on "+globals.port+" TCP port")

def menu_startgame_onserver():
    ''' finction called after the user click Connect to Server item '''
    globals.cli = True
    globals.ai = False
    globals.stage = 1
    globals.gameinformationpanel.show=False
def menu_starthotseatgame():
    globals.cli = False
    globals.ai = False
    globals.stage = 1
    globals.gameinformationpanel.show = False
def menu_options():
    ''' function called after the user click options menu item'''
    options.options_main()
def select_language(lang):
    globals.language = lang
    options.options_main()
    globals.gameinformationpanel.display('Save settings and restart the game to accept changes')
def menu_select_language():
    globals.background = pygame.image.load(current_folder+'/misc/menu_bg.jpg').convert_alpha()
    globals.background_backup = globals.background.copy()
    globals.menu_bg = pygame.image.load(current_folder+'/misc/menu_selections_bg.jpg').convert_alpha()
    menupos = globals.menu_bg.get_rect()
    menupos.centerx = globals.background.get_rect().centerx -2 # '-2' hack due lazy designer :)
    menupos.centery = globals.background.get_rect().centery -1 # '-1' hack due lazy designer :)
    globals.background.blit(globals.menu_bg, menupos)
    globals.menu_group.empty()
    MenuButton(0, "English", "select_language('en')")
    MenuButton(1, "Russian", "select_language('ru')")
    MenuButton(3, "Back", "options.options_main()")
    globals.menu_group.update()
def menu_main(): 
    ''' display Main manu '''

    #http://www.feebleminds-gifs.com/wizard-flames.jpg

    globals.background = pygame.image.load(current_folder+'/misc/menu_bg.jpg').convert_alpha()
    globals.background_backup = globals.background.copy()

    globals.menu_bg = pygame.image.load(current_folder+'/misc/menu_selections_bg.jpg').convert_alpha()
    menupos = globals.menu_bg.get_rect()
    menupos.centerx = globals.background.get_rect().centerx -2 # '-2' hack due lazy designer :)
    menupos.centery = globals.background.get_rect().centery -1 # '-1' hack due lazy designer :)
    globals.background.blit(globals.menu_bg, menupos)

    globals.menu_group.empty()
    menu1 = MenuButton(0,"Single Player","menu_startsinglegame()")
    menu2 = MenuButton(1,"Start Server","menu_startserver()")
    menu3 = MenuButton(2,"Multiplayer","menu_multiplayer()")
    menu4 = MenuButton(3,"Options","menu_options()")
    menu5 = MenuButton(6,"Quit","menu_esc_question()")

    globals.menu_group.update()
    #globals.background_backup = globals.background.copy()
def menu_multiplayer():
    globals.menu_group.empty()
    globals.background = pygame.image.load(globals.current_folder + '/misc/menu_bg.jpg').convert_alpha()
    globals.background_backup = globals.background.copy()
    globals.menu_bg = pygame.image.load(globals.current_folder + '/misc/menu_selections_bg.jpg').convert_alpha()
    menupos = globals.menu_bg.get_rect()
    menupos.centerx = globals.background.get_rect().centerx -2 # '-2' hack due lazy designer :)
    menupos.centery = globals.background.get_rect().centery -1 # '-1' hack due lazy designer :)
    globals.background.blit(globals.menu_bg, menupos)
    MenuButton(0,"HotSeat","menu_starthotseatgame()")
    MenuButton(1,"Online","menu_startgame_onserver()")
    MenuButton(3,"Cancel","menu_main()")

    globals.menu_group.update()
def exit_program():
    ''' handle a clean exit of threads '''
    globals.running = False
    if globals.cli: 
        if not globals.opponent_disconnect:
            sockets.query({"action":"bye","player_id":globals.player_id})
        else:
            sockets.query({"action":"bbye"})
    if globals.server_thread: 
        time.sleep(2) #wait for connect threads close itself
        #unblock server thread
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", int(globals.port)))
        sock.close()
        globals.server_thread.join(5)
    sys.exit(0)
