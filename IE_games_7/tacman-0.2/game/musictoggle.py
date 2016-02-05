"""Toggles music on and off"""

import serge.sound
import serge.blocks.utils
import serge.blocks.layout
import serge.blocks.visualblocks

from theme import G, theme

MUSIC_BUTTON = None
SOUND_BUTTON = None

def addToggle(world):
    """Add the toggle to the world"""
    global MUSIC_BUTTON, SOUND_BUTTON
    #
    # Block for sound menu
    sound_menu_block = serge.blocks.utils.addActorToWorld(world,
        serge.blocks.layout.VerticalBar('sound-menu-block', height=G('sound-menu-height'), width=G('sound-menu-width')), 
            layer_name='ui', center_position=G('sound-menu-position'))
    #
    if not MUSIC_BUTTON:
        music_button = serge.actor.Actor('music', 'music')
        music_button.visual = serge.blocks.visualblocks.TextToggle('', (255, 255, 255),
            'music-button')
        music_button.linkEvent(serge.events.E_LEFT_CLICK, musicToggle, music_button)
        if serge.sound.Music.isPaused():
            music_button.visual.setOff()
        MUSIC_BUTTON = music_button
    else:
        music_button = MUSIC_BUTTON
    #
    if not SOUND_BUTTON:
        sound_button = serge.actor.Actor('sound', 'sound')
        sound_button.visual = serge.blocks.visualblocks.TextToggle('', (255, 255, 255),
            'sound-button')
        sound_button.linkEvent(serge.events.E_LEFT_CLICK, soundToggle, sound_button)
        if serge.sound.Sounds.isPaused():
            sound_button.visual.setOff()
        SOUND_BUTTON = sound_button
    else:
        sound_button = SOUND_BUTTON
    #
    sound_menu_block.addActor(sound_button)
    sound_menu_block.addActor(music_button)

def musicToggle(obj, btn):
    """Toggle music on and off"""
    btn.visual.toggle()
    if btn.visual.isOff():
        serge.sound.Music.pause()
    else:
        serge.sound.Music.unpause()

def soundToggle(obj, btn):
    """Toggle sound on and off"""
    btn.visual.toggle()
    if btn.visual.isOff():
        serge.sound.Sounds.pause()
    else:
        serge.sound.Sounds.unpause()

