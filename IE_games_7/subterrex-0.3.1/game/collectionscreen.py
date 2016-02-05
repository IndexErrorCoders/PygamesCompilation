"""The screen for showing the users collection of named crystals"""

import random
import math
import pygame
import datetime
import textwrap

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors

if serge.common.PYMUNK_OK:
    import pymunk
    import serge.physical

from theme import G, theme
import common 
import cave
import player
import climbing
import mainscreen
import history
import tree

class CollectionScreen(serge.blocks.actors.ScreenActor):
    """The logic for the collection screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(CollectionScreen, self).__init__('item', 'collection-screen')
        self.options = options
        self.globals = serge.blocks.singletons.Store.getItem('globals')  
        self.current_page = None
        
    def addedToWorld(self, world):
        """The start screen was added to the world"""
        super(CollectionScreen, self).addedToWorld(world)
        #
        self.manager = world.findActorByName('behaviours')
        self.history = self.globals.history
        #
        # Logo
        the_theme = theme.getTheme('collection-screen')
        self.L = L = the_theme.getProperty
        logo = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'logo', 'icon', 'ui', 
            center_position=L('logo-position'))
        #
        # Background
        bh = serge.blocks.utils.addSpriteActorToWorld(world, 'bg', 'bg', L('screen-background-sprite'), 'background', 
            center_position=L('screen-background-position'))
        #
        serge.blocks.utils.addTextItemsToWorld(world, [
                    ('Your collection of named crystals', 'title'),
                    ('Next Page', 'next', self.nextPage),
                    ('Previous Page', 'previous', self.previousPage),
                    ('Page ...', 'page'),
                    ('Back', 'back', serge.blocks.utils.backToPreviousWorld('click')),
        ], the_theme, 'ui')
        #
        self.page = world.findActorByName('page')
        #
        # The grid
        self.grid = grid = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.layout.Grid('grid', 'grid', size=L('grid-size'), width=L('grid-width'),
                height=L('grid-height'), background_colour=L('background-colour')),
            center_position=L('grid-position'), layer_name='ui-back')
        #
        # Populate with slots
        w, h = L('grid-size')
        for x in range(w):
            for y in range(h):
                #
                # Layout of the labels
                slot = serge.blocks.layout.VerticalBar('slot', 'vbar', width=L('slot-width'), height=L('slot-height'),
                    background_colour=L('slot-background-colour'), background_layer='ui-back')
                grid.addActor((x, y), slot, 'ui')
                #
                # Text labels
                t1 = serge.blocks.actors.StringText(
                    'label', 'text', 'Title', colour=L('t1-colour'), font_size=L('t1-font-size'))
                t2 = serge.blocks.actors.StringText(
                    'label', 'text', 'Details', colour=L('t2-colour'), font_size=L('t2-font-size'))
                slot.addActor(t1)
                slot.addActor(t2)
                t1.setLayerName('ui')
                t2.setLayerName('ui')
                slot.long_description = ''
        #
        self.selected_slot = None
        #
        # Extra detail window
        self.detail = serge.blocks.utils.addVisualActorToWorld(world, 'text', 'detail',
            serge.blocks.visualblocks.RectangleText('Details', L('detail-colour'), 
                (L('detail-width'), L('detail-height')), L('detail-backcolour'), L('detail-font-size')),
                layer_name='overlay')
        self.detail.visible = False
        #
        # Trees
        tree.addTrees(L, world)
        #
        self.current_page = 0
        self.page_size = w*h
        self.page_width = w
        self.page_height = h
        self.populateCurrentPage()
        #
        self.world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.resetCamera)
    
    def resetCamera(self, obj, arg):
        """Reset camera position"""
        self.camera.moveTo(*G('screen-background-position', 'collection-screen'))
        if self.current_page is not None:
            self.populateCurrentPage()
        
    def updateActor(self, interval, world):
        """Update this actor"""
        super(CollectionScreen, self).updateActor(interval, world)
        #
        if self.keyboard.isClicked(pygame.K_ESCAPE):
            self.engine.goBackToPreviousWorld()
        #
        # Look out for mousing over a slot
        actors = self.mouse.getActorsUnderMouse(world).findActorsByTag('slot')
        self.unhighlightSlot()
        if actors:
            self.highlightSlot(actors[0])
        
    def populateCurrentPage(self):
        """Show the current page"""
        self.page.visual.setText('Page %d' % (self.current_page+1))
        #
        data = self.history.getNamedCrystals()
        #
        # Remove duplicates and sort by most recent
        trimmed_data = {}
        for _, name, description, cave_name, the_time in data:
            trimmed_data[name + description] = (the_time, name, description, cave_name)
        data = trimmed_data.values()
        data.sort()
        data.reverse()
        #
        page = data[self.current_page*self.page_size:(self.current_page+1)*self.page_size]
        #
        # Clear everything
        for item in self.world.getActors().findActorsByTags(['label', 'slot']):
            item.visible = False
        #
        x = y = 0
        for the_time, name, description, cave_name in page:
            #
            # Populate the cell
            slot = self.grid.getActorAt((x, y))
            slot.visible = True
            t1, t2 = slot.getChildren()
            t1.visual.setText(name)
            short_description = '\n'.join(textwrap.wrap( 
                'in %s on %s' % (
                    ('"%s"' % cave_name) if cave_name != 'RANDOM-CAVE' else 'an unknown cave', 
                    datetime.datetime.fromtimestamp(the_time).strftime('%m/%d')), 30))
            t2.visual.setText(short_description)
            slot.long_description = description
            #
            # Move to next cell
            x += 1
            if x == self.page_width:
                y += 1
                x = 0
            
 
    def nextPage(self, obj, arg):
        """Next page"""
        self.current_page += 1
        self.populateCurrentPage()   
        serge.sound.Sounds.play('ok-crystal')    

    def previousPage(self, obj, arg):
        """Previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.populateCurrentPage()       
            serge.sound.Sounds.play('ok-crystal')    

    def highlightSlot(self, slot):
        """Highlight a slot and show details"""
        slot.setBackgroundColour(self.L('slot-active-background-colour'))
        self.selected_slot = slot
        self.detail.visible = slot.visible
        self.detail.moveTo(slot.x, slot.y+slot.height/2+self.detail.height/2)
        self.detail.visual.text_visual.setText('\n'.join(textwrap.wrap(slot.long_description, self.L('detail-wrap'))))
        
    def unhighlightSlot(self):
        """Unhighlight a slot and hide details"""
        if self.selected_slot:
            self.selected_slot.setBackgroundColour(self.L('slot-background-colour'))
            self.selected_slot = None
            self.detail.visible = False
                
def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = CollectionScreen(options)
    world = serge.engine.CurrentEngine().getWorld('collection-screen')
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    world.addActor(s)
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    #
    # Screenshots
    if options.screenshot:
        manager.assignBehaviour(None, 
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_TAB, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

