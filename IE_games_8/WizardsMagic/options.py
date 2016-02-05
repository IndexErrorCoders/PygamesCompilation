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
try:
    import pygame
    from pygame.locals import *
    from widgets import TxtInput, CheckBox
    import menu
    yes_pygame = True
except ImportError:
    yes_pygame = False
import sys
import globals
import ConfigParser
import os.path
def launcher():
    #Something ,what we need to change after reset configuration
    try:
        globals.bg_sound.stop()
    except AttributeError:
        globals.bg_sound = pygame.mixer.Sound(globals.current_folder+'/misc/sounds/11_the_march_of_the_goblins__tobias_steinmann.ogg')
    if globals.music == "Y":
        globals.bg_sound.play(-1)
def save():
    config = ConfigParser.RawConfigParser()
    config.add_section('WizardsMagic')
    for item in globals.menu_group:
        if item.type=='txtinput':
            config.set('WizardsMagic', item.key, item.text)
        if item.type=='checkbox':
            config.set('WizardsMagic', item.key, (item.value and 'Y' or 'N'))
    config.set('WizardsMagic','language',globals.language)
    configfile=open(globals.current_folder + '/wizardsmagic.cfg', 'wb')
    config.write(configfile)
    configfile.close()
    read_configuration()
    launcher()
    menu.menu_main()

def cancel(): 
    menu.menu_main()

def read_configuration():
    config = ConfigParser.ConfigParser()
    config.read(globals.current_folder + '/wizardsmagic.cfg')

    try:
        globals.music = config.get('WizardsMagic', 'music')
        globals.music = globals.music.upper()
        if not globals.music in "YN":
            globals.music = "Y"
    except:
        globals.music = "Y"
    try:
        globals.sound = config.get('WizardsMagic', 'sound')
        globals.sound = globals.sound.upper()
        if not globals.sound in "YN":
            globals.sound = "Y"
    except:
        globals.sound = "Y"
    #try:
    #    globals.ai = config.get('WizardsMagic', 'ai')
    #    globals.ai = globals.ai.upper()
    #    if not globals.ai in "YN":
    #        globals.ai = "Y"
    #except:
    #    globals.ai = "Y"
    try:
        globals.nick = config.get('WizardsMagic', 'nick')
    except:
        globals.nick = "myname"
    try:
        globals.server = config.get('WizardsMagic', 'server')
    except:
        globals.server = "127.0.0.1"
    try:
        globals.port = config.getint('WizardsMagic', 'port')
        if globals.port<=0 or globals.port>65535:
            globals.port = 7712
        globals.port = str(globals.port)
    except:
        globals.port = "7712"
    try:
        globals.animation = config.get('WizardsMagic', 'animation')
        globals.animation = globals.animation.upper()
        if not globals.animation in "YN":
            globals.animation = "Y"
    except:
        globals.animation = "Y"
    try:
        globals.language
    except:
        try:
            globals.language = config.get('WizardsMagic', 'language')
            globals.language = globals.language.lower()
            if not globals.language in ['ru','en']:
                globals.language = 'en'
        except:
            globals.language = 'en'
def options_main(): 
    ''' display options menu '''

    globals.menu_group.empty()
    globals.background = pygame.image.load(globals.current_folder + '/misc/menu_bg.jpg').convert_alpha()
    globals.background_backup = globals.background.copy()
    globals.menu_bg = pygame.image.load(globals.current_folder + '/misc/menu_selections_bg.jpg').convert_alpha()
    menupos = globals.menu_bg.get_rect()
    menupos.centerx = globals.background.get_rect().centerx -2 # '-2' hack due lazy designer :)
    menupos.centery = globals.background.get_rect().centery -1 # '-1' hack due lazy designer :)
    globals.background.blit(globals.menu_bg, menupos)

    #Configuration file:
    #create default configuration file
    if not os.path.isfile(globals.current_folder + '/wizardsmagic.cfg'):
        config = ConfigParser.RawConfigParser()
        config.add_section('WizardsMagic')
        config.set('WizardsMagic', 'music', 'Y')
        config.set('WizardsMagic', 'sound', 'Y')
        config.set('WizardsMagic', 'nick', 'myname')
        config.set('WizardsMagic', 'server', '127.0.0.1')
        config.set('WizardsMagic', 'port', '7712')
        config.set('WizardsMagic', 'language', 'en')
        #config.set('WizardsMagic', 'ai', 'Y')
        config.set('WizardsMagic', 'animation', 'Y')
        configfile = open(globals.current_folder + '/wizardsmagic.cfg', 'wb')
        config.write(configfile)
        configfile.close()

    #read configuration file
    read_configuration()
    option1 = CheckBox(2,"MUSIC:", (globals.music == 'Y'), key="music")
    option1 = CheckBox(1,"SOUNDS:", (globals.sound == 'Y'), key="sound")
    option0 = CheckBox(0, "ANIMATION:", (globals.animation == 'Y'), key='animation')
    option2 = TxtInput(3,"NICK:", globals.nick, 8, key="nick")
    option3 = TxtInput(4,"SERVER:", globals.server, 15, key="server")
    option4 = TxtInput(5,"PORT:", globals.port, 5, key="port")
    option5 = menu.MenuButton(5, "Select language", "menu_select_language()")
    #option5 = CheckBox(6, "AI:", (globals.ai == 'Y'), key="ai")
    option6 = menu.MenuButton(-1, "SAVE", "options.save()", loc=(70, menupos.height-50))
    option7 = menu.MenuButton(-1, "CANCEL", "options.cancel()", loc=(160, menupos.height-50))
    globals.menu_group.update()

