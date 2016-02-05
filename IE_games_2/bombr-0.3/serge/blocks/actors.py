"""Blocks to help with actors"""

import sys
import pygame
import random

import serge.actor
import serge.engine
import serge.actor
import serge.input
import serge.events
import serge.sound
import serge.visual
import serge.blocks.behaviours
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.animations


class InvalidMenu(Exception): """The menu was not valid"""
class InvalidMenuItem(Exception): """The menu item was not understood"""
class BadRange(Exception): """Data was in a bad range"""


class ScreenActor(serge.actor.CompositeActor):
    """An actor to represent the logic associated with a screen of the game
    
    This actor is useful when encapsulating the logic associated with a specific
    screen in the game. The actor has useful properties and methods that
    make it easy to manage the logic.
    
    """

    def __init__(self, *args, **kw):
        """Initialise the ScreenActor"""
        super(ScreenActor, self).__init__(*args, **kw)
        
    def addedToWorld(self, world):
        """The actor was added to the world"""
        super(ScreenActor, self).addedToWorld(world)
        self.world = world
        self.engine = serge.engine.CurrentEngine()
        self.keyboard = self.engine.getKeyboard()
        self.mouse = self.engine.getMouse()
        self.camera = self.engine.getRenderer().getCamera()
        self.broadcaster = serge.events.getEventBroadcaster()
        

class RepeatedVisualActor(serge.blocks.animations.AnimatedActor):
    """An actor that shows multiple copies of a visual representation
    
    This actor is useful for showing the number of lives or missiles
    etc in a game.
    
    """

    def __init__(self, tag, name=None, repeat=5, spacing=10, orientation='horizontal'):
        """Initialise the RepeatedVisualActor"""
        super(RepeatedVisualActor, self).__init__(tag, name)
        self._repeat = repeat
        self._spacing = spacing
        self._current = repeat
        self._orientation = orientation

    def _resetVisual(self):
        """Reset the visual item on the center point
        
        We need to override this because our size is not determined by our visual
        
        """
        #
        # Adjust our location so that we are positioned and sized appropriately
        cx, cy, _, _ = self.getSpatialCentered()
        #
        if self._orientation == 'horizontal':
            self.setSpatialCentered(
                cx, cy,
                self._visual.width + self._spacing * (self._repeat - 1), self._visual.height)
        else:
            self.setSpatialCentered(
                cx, cy,
                self._visual.width, self._visual.height + self._spacing * (self._repeat - 1))
            #
        # Here is a hack - sometimes the visual width changes and we want to update our width
        # so we let the visual know about us so it can update our width. This is almost 
        # certainly the wrong thing to do, but we have some tests in there so hopefully
        # the right thing becomes obvious later!
        self._visual._actor_parent = self
        
    def renderTo(self, renderer, interval):
        """Render to the given renderer"""
        if self._visual:
            layer = renderer.getLayer(self.layer)
            camera = renderer.camera
            if layer.static:
                ox, oy = self.getOrigin()
            elif camera.canSee(self):
                ox, oy = camera.getRelativeLocation(self)
            else:
                # Cannot see me
                return
            if self.layer:
                for i in range(self._current):
                    if self._orientation == 'horizontal':
                        x, y = (ox + i*self._spacing, oy)
                    else:
                        x, y = (ox, oy + i*self._spacing)
                    self._visual.renderTo(interval, renderer.getLayer(self.layer).getSurface(), (x, y))

    def reduceRepeat(self, amount=1):
        """Reduce the repeat by a certain amount"""
        self.setRepeat(self._current - amount)
        
    def increaseRepeat(self, amount=1):
        """Increase the repeat by a certain amount"""
        self.setRepeat(self._current + amount)
        
    def getRepeat(self):
        """Return the current repeat"""
        return self._current

    def setRepeat(self, value):
        """Set the current repeat"""
        if self._current != value:
            self._current = value
            #
            # Reset the visual size
            ox, oy, w, h = self.getSpatial()
            if self._orientation == 'horizontal':
                w = self._visual.width + self._spacing*(self._current-1)
            else:
                h = self._visual.height + self._spacing*(self._current-1)
            self.setSpatial(ox, oy, w, h)
            self.log.debug('New spatial = %s' % self.getSpatial())
        
    def resetRepeat(self):
        """Reset the repeat to the initial value"""
        self.setRepeat(self._repeat)
        
        
class FormattedText(serge.blocks.animations.AnimatedActor):
    """A text display that can be formatted"""

    def __init__(self, tag, name, format, colour, font_name='DEFAULT', font_size=12, justify='center',
                 fixed_char_width=None, **kw):
        """Initialise the text"""
        super(FormattedText, self).__init__(tag, name)
        self.visual = serge.visual.Text('', colour, font_name, font_size, justify,
                                        fixed_char_width=fixed_char_width)
        self.format = format
        self.values = kw
        self.updateText()
        
    def updateText(self):
        """Update our text"""
        self.visual.setText(self.format % self.values)

    def setValue(self, name, value):
        """Set the value"""
        if self.values.get(name, None) != value:
            self.values[name] = value
            self.updateText()
            
    def getValue(self, name):
        """Get the values"""
        return self.values[name]


class NumericText(FormattedText):
    """A helper actor to display some text with a single number in there"""

    def __init__(self, *args, **kw):
        """Initialise the text"""
        super(NumericText, self).__init__(*args, **kw)
        
    def updateText(self):
        """Update our text"""
        self.visual.setText(self.format % self.values['value'])

    @property
    def value(self): return self.getValue('value')

    @value.setter
    def value(self, v): self.setValue('value', v)


class StringText(FormattedText):
    """A helper actor to display some text with text in there"""

    def __init__(self, tag, name, text, format='%s', colour=(255, 255, 255), font_name='DEFAULT', font_size=12,
                 justify='center', **kw):
        """Initialise the text"""
        super(StringText, self).__init__(tag, name, format, colour, font_name, font_size, justify, value=text, **kw)
        
    def updateText(self):
        """Update our text"""
        self.visual.setText(self.format % self.values['value'])

    @property
    def value(self): return self.getValue('value')

    @value.setter
    def value(self, v): self.setValue('value', v)


class MuteButton(serge.actor.Actor):
    """A button to mute sound"""

    def __init__(self, sprite_name, layer_name, mute_sound=True, mute_music=True, alpha=1.0):
        """Initialise the button"""
        super(MuteButton, self).__init__('mute-button', 'mute-button')
        self.mute_sound = mute_sound
        self.mute_music = mute_music
        self.setSpriteName(sprite_name)
        self.setLayerName(layer_name)
        self.visual.setAlpha(alpha)
        self.linkEvent(serge.events.E_LEFT_CLICK, self.toggleSound)
        
    def toggleSound(self, obj=None, arg=None):
        """Clicked on the button"""
        if self.mute_sound:
            serge.sound.Sounds.toggle()
        if self.mute_music:
            serge.sound.Music.toggle()
        self.visual.setCell(1 if self.visual.getCell() == 0 else 0)


class ToggledMenu(serge.actor.MountableActor):
    """Implements a menu of options that can be toggled
    
    The layout of the options will be determined by the layout object. Items will
    be added to the layout in the order they are specified.
    
    The callback provided will be called whenever the selection changes. The function
    will be called with the menu object and the name of the option selected.
        
        callback(menuObject, newOption)
    
    """

    def __init__(self, tag, name, items, layout, default, on_colour, off_colour, 
                    width=100, height=100, callback=None, font_colour=(255, 255, 255, 255), 
                    font_name='DEFAULT', font_size=12, mouse_over_colour=None):
        """Initialise the ToggledMenu"""
        super(ToggledMenu, self).__init__(tag, name)
        #
        # Reality check
        if not items:
            raise InvalidMenu('Menu must have at least one item in it')
        if len(set(items)) != len(items):
            raise InvalidMenu('Menu cannot have duplicates in it (%s)' % (', '.join(items)))         
        #
        # Setup the menu
        self.mountActor(layout, (0, 0))
        self.on_colour = on_colour
        self.off_colour = off_colour
        self.mouse_over_colour = mouse_over_colour
        self.callback = callback
        self.layout = layout
        #
        self._moused_over_item = None
        #
        self.menu_width = width
        self.menu_height = height
        self.menu_font_colour = font_colour
        self.menu_font_name = font_name
        self.menu_font_size = font_size
        #
        self.setupMenu(items)
        self.selectItem(default)

    def setupMenu(self, items):
        """Setup all the menu items"""
        self.layout.removeChildren()
        self._menu_items = {}
        self.items = items
        self._selection = None
        #
        for idx, item in enumerate(items):
            new_item = serge.actor.Actor(('%s-menuitem' % self.name), '%s-item-%s' % (self.name, idx))
            new_item.visual = serge.blocks.visualblocks.RectangleText(
                    item, self.menu_font_colour, (self.menu_width, self.menu_height), self.off_colour,
                    font_size=self.menu_font_size, font_name=self.menu_font_name)
            self._menu_items[item] = new_item
            self.layout.addActor(new_item)
            new_item.linkEvent(serge.events.E_LEFT_CLICK, self._itemClick, item)

    def updateActor(self, interval, world):
        """Update the actor"""
        super(ToggledMenu, self).updateActor(interval, world)
        #
        # Check for mouse over
        if self.mouse_over_colour:
            mouse_pos = serge.engine.CurrentEngine().getMouse().getScreenPoint()
            for idx, item in enumerate(self._menu_items.values()):
                #
                # Moused over and a new item?
                if mouse_pos.isInside(item):
                    if item != self._moused_over_item:
                        self._highlightItem(item, self.mouse_over_colour, self.off_colour, skip_selected=True)
                        self._moused_over_item = item
                    break
            else:
                #
                # Nothing is moused over - so clear if needed
                if self._moused_over_item:
                    self._highlightItem(None, self.mouse_over_colour, self.off_colour, skip_selected=True)
                    self._moused_over_item = None

    def setLayerName(self, layer_name):
        """Set the layer name"""
        super(ToggledMenu, self).setLayerName(layer_name)
        #
        self.layout.setLayerName(layer_name)
            
    def selectItem(self, name, do_callback=True):
        """Select an item by name"""
        #
        # Don't select if already selected
        if name == self._selection or name is None:
            return
        #
        try:
            the_item = self._menu_items[name]
        except KeyError:
            raise InvalidMenuItem('Menu item "%s" not found in menu %s' % (name, self.getNiceName()))
        self._highlightItem(the_item, self.on_colour, self.off_colour)
        #
        self._selection = name
        if self.callback and do_callback:
            self.callback(self, name)

    def _highlightItem(self, the_item, on_colour, off_colour, skip_selected=False):
        """Highlight an item"""
        #
        # Highlight items
        selected_item = self._menu_items.get(self.getSelection(), None)

        for idx, item in enumerate(self._menu_items.values()):
            if skip_selected and item == selected_item:
                continue
            item.visual.rect_visual.colour = on_colour if item is the_item else off_colour

    def selectItemIndex(self, index):
        """Select an item by its index"""
        try:
            name = self.items[index]
        except IndexError:
            raise InvalidMenuItem('Index %s is outside the range of menu %s' % (index, self.getNiceName()))
        self.selectItem(name)
        
    def getSelection(self):
        """Return the current selection"""
        return self._selection
        
    def getSelectionIndex(self):
        """Return the current selection index"""
        return -1 if self._selection is None else self.items.index(self._selection)
        
    def _itemClick(self, obj, name):
        """Clicked on an item"""
        self.selectItem(name)   
        #
        # Don't propagate click
        return serge.events.E_LEFT_CLICK
    
    def clearSelection(self):
        """Clear the active selection"""
        self._selection = None
        #
        # Highlight items
        for item in self._menu_items.values():
            item.visual.rect_visual.colour = self.off_colour
        

class AnimateThenDieActor(serge.actor.Actor):
    """An actor that shows its animation and then is removed from the world"""

    def __init__(self, tag, name, sprite_name, layer_name, parent=None):
        """Initialise the AnimateThenDieActor
        
        If the parent is specified then we will be moved to the location of the parent
        
        """
        super(AnimateThenDieActor, self).__init__(tag, name)
        #
        self.parent = parent
        self.setSpriteName(sprite_name)
        self.setLayerName(layer_name)
        
    def addedToWorld(self, world):
        """Added the actor to the world"""
        super(AnimateThenDieActor, self).addedToWorld(world)
        #
        if self.parent:
            self.moveTo(self.parent.x, self.parent.y)
            
    def updateActor(self, interval, world):
        """Update the actor"""
        if not self.visual.running:
            # Ok, run its course
            world.scheduleActorRemoval(self)


class FPSDisplay(NumericText):
    """Displays the current FPS on the screen"""
    
    def __init__(self, x, y, font_colour, font_size, font_name='DEFAULT'):
        """Initialise the FPS display"""
        super(FPSDisplay, self).__init__('fps', 'fps', 'FPS: %5.2f', colour=font_colour, font_size=font_size,
            value=0, font_name=font_name)
        self.setLayerName('ui')
        self.engine = serge.engine.CurrentEngine()
        self.ix = x
        self.iy = y
        
    def addedToWorld(self, world):
        """Added to the world"""
        super(FPSDisplay, self).addedToWorld(world)
        #
        self.moveTo(self.ix, self.iy)  
        
    def updateActor(self, interval, world):
        """Update the actor"""
        super(FPSDisplay, self).updateActor(interval, world)
        self.value = self.engine.getStats().average_frame_rate
        

class TextEntryWidget(serge.actor.MountableActor):
    """Implements a single line text entry widget
    
    Support letters and numbers. Delete, backspace and left all delete the last
    character. Enter triggers an ACCEPT event.
    
    """
    
    def __init__(self, tag, name, width, height, colour, font_size, font_name='DEFAULT', 
                    justify='center', background_visual=None, background_layer='background',
                    show_cursor=False, blink_time=0.5, has_focus=True):
        """Initialise the text entry widget"""
        super(TextEntryWidget, self).__init__(tag, name)
        #
        # The text to display
        self.text = self.mountActor(StringText(tag, '%s-text' % name, '', colour=colour, font_name=font_name,
            font_size=font_size, justify=justify), (0, 0))
        #
        # Our background
        if background_visual:
            self.background = self.mountActor(serge.actor.Actor(tag, '%s-bg' % name), (0, 0))
            self.background.visual = background_visual
            self.background.setLayerName(background_layer)
        #
        self.show_cursor = show_cursor
        self.colour = colour
        self.font_name = font_name
        self.blink_time = blink_time
        self.has_focus = has_focus
        self.cursor_pos = 0
        #
        self.resizeTo(width, height)
        #
        # Set keys
        if sys.platform != 'darwin':
            self._delete_key = pygame.K_DELETE
            self._backspace_key = pygame.K_BACKSPACE
        else:
            self._delete_key = 63272
            self._backspace_key = pygame.K_DELETE

    def setLayerName(self, layer_name):
        """Set the layer name"""
        super(TextEntryWidget, self).setLayerName(layer_name)
        #
        self.text.setLayerName(layer_name)

    def addedToWorld(self, world):
        """Added to the world"""
        super(TextEntryWidget, self).addedToWorld(world)
        #
        self.keyboard = serge.engine.CurrentEngine().getKeyboard() 
        #
        # The cursor
        if self.show_cursor:
            #
            # Create the cursor
            font = self.text.visual.font
            w, h = font.size('#')
            self.cursor = serge.actor.Actor(self.tag, '%s-cursor' % self.name)
            self.cursor.visual = serge.blocks.visualblocks.Rectangle((w, h), self.colour)
            self.cursor.setLayerName(self.getLayerName())
            self.addChild(self.cursor)
            self.cursor.setLayerName(serge.engine.CurrentEngine().getRenderer().getBackgroundLayer().name)
             #
            # And make it blink
            manager = world.findActorByName('behaviours')
            manager.assignBehaviour(self.cursor, serge.blocks.behaviours.Blink(
                self.cursor, self.blink_time), 'blinking')
        else:
            self.cursor = None
                
    def updateActor(self, interval, world):
        """Update the entry widget"""
        #
        # Handle the keystrokes
        if self.has_focus:
            #
            # Letters
            entered = self.keyboard.getTextEntered()
            for typ, value in entered:
                if typ == serge.input.K_LETTER:
                    key = ord(value)
                    if key == self._backspace_key:
                        self._backspace()
                    elif key == self._delete_key:
                        self._delete()
                    elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.processEvent((serge.events.E_ACCEPT_ENTRY, self.text.value))
                    elif key in (pygame.K_ESCAPE,):
                        self.has_focus = False
                    elif key in (pygame.K_TAB,):
                        pass 
                    else:
                        self.cursor_pos += 1
                        self.text.value = self.text.value[0:self.cursor_pos-1] + value + self.text.value[self.cursor_pos-1:]
                elif typ == serge.input.K_CONTROL:
                    if value == pygame.K_LEFT:
                        self.cursor_pos = max(0, self.cursor_pos-1)
                    elif value == pygame.K_RIGHT:
                        self.cursor_pos = min(len(self.text.value), self.cursor_pos+1)
                    elif value in (pygame.K_UP, pygame.K_HOME):
                        self.setCursorAtStart()
                    elif value in (pygame.K_DOWN, pygame.K_END):
                        self.setCursorAtEnd()
                else:
                    raise ValueError('Unknown key type "%s"' % typ)
        #
        # Position the cursor if we have one
        if self.cursor:
            self.cursor.setLayerName(self.getLayerName())
            font = self.text.visual.font
            position = font.size(self.text.value)[0]/2 - font.size(self.text.value[self.cursor_pos:])[0]
            self.cursor.moveTo(self.text.x + position + self.cursor.width/2, self.text.y)
            self.cursor.active = self.hasFocus()

    def getText(self):
        """Return the text value"""
        return self.text.value
        
    def setText(self, text):
        """Set the text value"""
        self.text.value = str(text)

    def getFocus(self):
        """Get the focus"""
        self.has_focus = True
        self.cursor_pos = len(self.text.value)
        
    def loseFocus(self):
        """Lose the focus"""
        self.has_focus = False
        
    def hasFocus(self):
        """Return True if we have focus"""
        return self.has_focus

    def setCursorAtStart(self):
        """Set the cursor at the start position"""
        self.cursor_pos = 0

    def setCursorAtEnd(self):
        """Set the cursor at the end position"""
        self.cursor_pos = len(self.text.value)

    def _backspace(self):
        """Do a backspace"""
        if self.cursor_pos > 0: 
            self.text.value = self.text.value[0:self.cursor_pos-1] + self.text.value[self.cursor_pos:]
            self.cursor_pos = max(0, self.cursor_pos-1)

    def _delete(self):
        """Do a delete"""
        if self.cursor_pos < len(self.text.value): 
            self.text.value = self.text.value[0:self.cursor_pos] + self.text.value[self.cursor_pos+1:]

        
class FocusManager(serge.actor.CompositeActor):
    """Manages focus between a number of entry widgets"""

    def __init__(self, tag, name):
        """Initialise the FocusManager"""
        super(FocusManager, self).__init__(tag, name)
        #
        self._last_focus = None

    def addedToWorld(self, world):
        """We were added to the world"""
        super(FocusManager, self).addedToWorld(world)
        #
        self.keyboard = serge.engine.CurrentEngine().getKeyboard()
        
    def addChild(self, actor):
        """Add an actor to the manager"""
        super(FocusManager, self).addChild(actor)
        #
        actor.linkEvent(serge.events.E_LEFT_CLICK, self.actorSelected, actor)
        actor.linkEvent(serge.events.E_ACCEPT_ENTRY, self.actorEntry, actor)
        
    def actorSelected(self, obj, actor):
        """An actor was selected"""
        self.log.debug('Focus set to %s' % actor.getNiceName())
        #
        # Defocus
        self.getChildren().forEach().loseFocus()
        if self._last_focus:
            self.processEvent((serge.events.E_LOST_FOCUS, self._last_focus))
        #
        # Refocus
        if actor:
            actor.getFocus()
            self.processEvent((serge.events.E_GOT_FOCUS, actor))
        self._last_focus = actor
        
    def actorEntry(self, obj, actor):
        """An entry was accepted"""
        self.log.debug('Entry to %s' % actor.getNiceName())
        self.processEvent((serge.events.E_ACCEPT_ENTRY, actor))
        # Defocus
        self.getChildren().forEach().loseFocus()

    def resetFocus(self):
        """Reset the focus to make sure it is on an active object

        Call this when you are altering the activity of different items
        in the focus group.

        """
        #
        # Find an active actor
        for actor in self.getChildren():
            if actor.active:
                self.actorSelected(None, actor)
                break
        else:
            #
            # No active actors - cancel focus
            self.actorSelected(None, None)

    def updateActor(self, interval, world):
        """Update the manager"""
        super(FocusManager, self).updateActor(interval, world)
        #
        # Watch for tab
        if self.keyboard.isClicked(pygame.K_TAB):
            children = self.getChildren()
            if children:
                # Find current focus
                focus = [actor for actor in children if actor.hasFocus()]
                #
                # Nobody has focus yet
                if len(focus) == 0:
                    focus_item = children[0 if not self.keyboard.isShiftDown() else -1]
                else:   
                    #
                    # Advance the focus
                    pos = children.index(focus[0])
                    if not self.keyboard.isShiftDown():
                        # Unshifted
                        if pos == len(children)-1:
                            focus_item = children[0]
                        else:
                            focus_item = children[pos+1]
                    else:
                        # Shifted
                        if pos == 0:
                            focus_item = children[-1]
                        else:
                            focus_item = children[pos-1]
                    self.actorSelected(None, focus_item)
 
class SimplePhysicsActor(serge.blocks.animations.AnimatedActor):
    """An actor that obeys simple physics of motion and rotation"""

    def __init__(self, name, tag, velocity, angular_velocity, bounds=None, gravity=None):
        """Initialise the SimplePhysicsActor"""
        super(SimplePhysicsActor, self).__init__(name, tag)
        self.velocity = velocity
        self.angular_velocity = angular_velocity
        self.bounds = bounds
        self.gravity = gravity

    def updateActor(self, interval, world):
        """Update the actor"""
        super(SimplePhysicsActor, self).updateActor(interval, world)
        #
        # Linear equation of motion
        if self.gravity:
            self.velocity += self.gravity * interval / 1000.0
        dx, dy = interval / 1000.0 * self.velocity
        self.move(dx, dy)
        #
        # Angular equation of motion
        da = interval / 1000.0 * self.angular_velocity
        self.setAngle(self.getAngle() + da)
        #
        # Check for in bounds
        if self.bounds:
            (minx, maxx), (miny, maxy) = self.bounds
            if not ((minx <= self.x <= maxx) and (miny <= self.y <= maxy)):
                self.log.debug('Removing physics actor %s - out of bounds' % self.getNiceName())
                world.scheduleActorRemoval(self)


class FullScreenMenu(serge.actor.MountableActor):
    """A full screen menu"""

    def __init__(self, tag, name, items, layout, callback, background_colour=(0, 0, 0),
                 font_colour=(255, 255, 255), font_size=12, font_name='DEFAULT'):
        """Initialise the menu"""
        super(FullScreenMenu, self).__init__(tag, name)
        #
        self.background_colour = background_colour
        self.font_colour = font_colour
        self.font_size = font_size
        self.font_name = font_name
        self.layout = layout
        self.items = items
        self.callback = callback
        #
        sx, sy = serge.engine.CurrentEngine().getRenderer().getScreenSize()
        self.moveTo(sx / 2, sy / 2)
        #
        # Background
        self.bg = self.mountActor(serge.actor.Actor('menu', 'bg'), (0, 0))
        self.bg.visual = serge.blocks.visualblocks.Rectangle(
            (sx, sy), self.background_colour
        )
        self.bg.linkEvent(serge.events.E_LEFT_CLICK, lambda o, a: serge.events.E_LEFT_CLICK)
        #
        # Layout
        self.mountActor(self.layout, (0, 0))
        #
        # Options
        for idx, item in enumerate(self.items):
            actor = self.layout.addActor(StringText(
                'menu', 'item-%d' % idx, item,
                colour=self.font_colour,
                font_name=self.font_name,
                font_size=self.font_size
            ))
            actor.linkEvent(serge.events.E_LEFT_CLICK, self.menuClick, item)

    def menuClick(self, obj, arg):
        """Menu item was clicked"""
        self.log.debug('Menu clicked on option "%s"' % arg)
        self.selected = arg
        self.callback(arg)
        #
        return serge.events.E_LEFT_CLICK

    def setLayerName(self, name):
        """Set the layer for the menu"""
        for child in self.getChildren():
            child.setLayerName(name)


class Timer(serge.actor.Actor):
    """A timer that goes off and calls a callback - time is in seconds"""

    def __init__(self, tag, name, least_time, most_time=None, callback=None, one_shot=False, started=True):
        """Initialise the timer"""
        super(Timer, self).__init__(tag, name)
        #
        self.least_time = least_time
        self.most_time = most_time
        self.callback = callback
        self.one_shot = one_shot
        #
        # Sanity check
        if most_time is not None and least_time > most_time:
            raise BadRange('Most time (%s) must be greater than least time (%s)' % (
                most_time, least_time
            ))
        #
        self._running = started
        self.setTimeToGo()
        self._time_passed = 0

    def setTimeToGo(self):
        """Set the time to go"""
        self._time_to_go = self._getTimeToGo()
        self.log.debug('Timer %s new time to go is %s' % (self.getNiceName(), self._time_to_go))

    def _getTimeToGo(self):
        """Return the time to go"""
        if self.most_time is None or self.least_time == self.most_time:
            return self.least_time
        else:
            return random.uniform(self.least_time, self.most_time)

    def updateActor(self, interval, world):
        """Update the timer"""
        if self._running:
            self._time_passed += interval / 1000.0
            #
            # Timer gone off?
            while self._time_passed >= self._time_to_go:
                self.log.debug('Timer %s has gone off' % self.getNiceName())
                self._time_passed -= self._time_to_go
                self.callback()
                #
                # One shots should just stop now
                if self.one_shot:
                    self.stopTimer()
                    break
                #
                # Get a new time to go
                self._time_to_go = self._getTimeToGo()

    def startTimer(self):
        """Start the timer"""
        self._running = True

    def stopTimer(self):
        """Stop the timer"""
        self._running = False

    def resetTimer(self):
        """Reset the timer back to zero

        If running then the timer continues to run. The time
        to go is recalculated

        """
        self._time_passed = 0
        self._time_to_go = self._getTimeToGo()

    def resetAndStopTimer(self):
        """Reset and stop the timer"""
        self.resetTimer()
        self.stopTimer()

    def resetAndStartTimer(self):
        """Reset and start the timer"""
        self.resetTimer()
        self.startTimer()