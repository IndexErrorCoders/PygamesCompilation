"""The head up display"""

import serge.blocks.actors
import serge.blocks.utils
import serge.blocks.layout

from theme import G, theme
import common 

class HUD(serge.blocks.actors.ScreenActor):
    """Implements a head up display of status items"""

    def __init__(self, tag, name, status):
        """Initialise the HUD"""
        super(HUD, self).__init__(tag, name)
        #
        self.status = status
        
    def addedToWorld(self, world):
        """Added the HUD to the world"""
        super(HUD, self).addedToWorld(world)
        #
        # Main layout panel
        self.main_panel = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.layout.VerticalBar('bar', 'main-bar', width=G('hud-width'), height=G('hud-height'),
                background_colour=G('hud-background-colour'), background_layer='ui-back'),                
            layer_name='ui',
            center_position=G('hud-position'))
        #
        # Other panels
        self.top_panel = serge.blocks.layout.HorizontalBar('bar', 'top-bar', width=G('hud-display-width'), height=G('hud-height')/2)
        self.bottom_panel = serge.blocks.layout.HorizontalBar('bar', 'bottom-bar', width=G('hud-width'), height=G('hud-height')/2)
        self.main_panel.addActor(self.top_panel)
        self.main_panel.addActor(self.bottom_panel)
        #
        # Time
        self.time = self.top_panel.addActor(serge.blocks.actors.FormattedText('text', 'time', '%(mins)02d:%(secs)02d', 
            G('hud-text-colour'), font_name=G('hud-font-name'), font_size=G('hud-font-size'), mins=0, secs=0))
        self.time_icon = self.top_panel.addActor(serge.actor.Actor('timer', 'timer'))
        self.time_icon.setSpriteName('timer')
        self.top_panel.addBlanks(1)
        #
        # Crystals
        self.crystals = self.top_panel.addActor(serge.blocks.actors.FormattedText('text', 'crystals', '%(got)d/%(total)d ', 
            G('hud-text-colour'), font_name=G('hud-font-name'), font_size=G('hud-font-size'), got=0, total=0))
        self.crystals_icon = self.top_panel.addActor(serge.actor.Actor('crystals', 'crystals'))
        self.crystals_icon.setSpriteName('big-crystal')
        self.top_panel.addBlanks(1)
        #
        # Ropes
        self.ropes = self.top_panel.addActor(serge.blocks.actors.NumericText('text', 'ropes', '%d Ropes', G('hud-text-colour'),
            font_name=G('hud-font-name'), font_size=G('hud-font-size'), value=self.status.ropes))
        self.camera_lock = self.top_panel.addActor(serge.blocks.actors.StringText('text', 'camera', '', '%s', 
            G('hud-text-colour'), font_name=G('hud-font-name'), font_size=G('hud-font-size')))
        #
        # The light information
        self.lights = {}
        for colour in ('yellow', 'green', 'blue'):
            self.lights['light-%s' % colour] = light = self.bottom_panel.addActor(
                serge.actor.Actor('light', '%s-light' % colour))
            light.setSpriteName('%s-light' % colour)
            light.linkEvent(serge.events.E_LEFT_CLICK, self.setSelection, colour)
            self.lights['number-%s' % colour] = self.bottom_panel.addActor(
                serge.blocks.actors.NumericText('text', 'number-%s' % colour, '%d', G('hud-%s-colour' % colour),
                    font_name=G('hud-font-name'), font_size=G('hud-light-font-size'), value=6))
        #
        self.highlight = serge.blocks.utils.addVisualActorToWorld(world, 'highlight', 'highlight',
            serge.blocks.visualblocks.Rectangle((G('hud-highlight-width'), G('hud-highlight-height')), (0,0,0,0)),
            layer_name='ui-highlight')
        self.highlight.visible = False
            
    def updateActor(self, interval, world):
        """Update the HUD"""
        super(HUD, self).updateActor(interval, world)
        #
        # Update the status indicators
        self.ropes.value = self.status.ropes
        self.time.setValue('mins', self.status.time_spent // 60)
        self.time.setValue('secs', self.status.time_spent % 60)
        self.crystals.setValue('got', self.status.collected_crystals)
        self.crystals.setValue('total', self.status.total_crystals)
        #
        # Lights
        for colour in ('yellow', 'green', 'blue'):
            self.lights['number-%s' % colour].value = self.status.getNumberOfLights(colour)
        self.camera_lock.value = '' if not self.status.camera_locked else 'L'
        #
        # Fade the highlight if needed
        if self.highlight.visible:
            r, g, b, a = self.highlight.visual.colour
            if a > 20:
                self.highlight.visual.colour = (r, g, b, a/2.0)
            else:
                self.highlight.visible = False
            
        
    def setSelection(self, obj, colour):
        """Set the selected light colour"""
        self.log.debug('Setting current colour to %s' % colour)
        light = self.lights['light-%s' % colour]
        self.highlight.setOrigin(*light.getOrigin())
        base_colour = G('colour', colour)
        self.highlight.visual.colour = base_colour+ (G('hud-highlight-opacity'),)
        self.highlighted_colour = colour
        self.highlight.visible = True
        #
        # Transmit event
        self.processEvent((common.E_ADD_LIGHT, colour))
        #
        # Return the event to inhibit others from handling it
        return serge.events.E_LEFT_CLICK
        
    def getCurrentColour(self):
        """Return the current colour of light"""
        return self.highlighted_colour
        
