"""Handle interaction with keyboard and mouse"""

import pygame
import common
import actor
import render
import geometry
pymunk = common.pymunk

#These represent mouse states we can query.
M_LEFT = 1
M_MIDDLE = 2
M_RIGHT = 3
M_WHEEL_UP = 4
M_WHEEL_DOWN = 5

#Represents the Keyboard and Mouse enums
KEYBOARD = 0
MOUSE = 1

#Type of key
K_LETTER = 0
K_CONTROL = 1


class KeyState(object):
    """Represents the state of keyboard keys"""
    
    def __init__(self):
        """Initialise the state"""
        self.key_states = []

    def getCopy(self):
        """Return a new copy of the key states"""
        new_keys = []
        for key in self.key_states:
            new_keys.append(key)
        state_cpy = KeyState()
        state_cpy.key_states = new_keys
        return state_cpy

    def getState(self, key):
        """Return the state of a specific key"""
        try:
            return self.key_states[key]
        except IndexError:
            return None

    def setState(self, key, state):
        """Set the state for a key"""
        states = list(self.key_states)
        states[key] = state
        self.key_states = tuple(states)


class Keyboard(common.Loggable):
    """Represents the state of the keyboard"""
    
    def __init__(self):
        """Initialise the keyboard"""
        super(Keyboard, self).__init__()
        self.addLogger()
        self.current_state = KeyState()
        self.previous_state = KeyState()
        self.current_state.key_states = pygame.key.get_pressed()
        self.text_entered = []

    def isDown(self, key):
        """Return True if the key is down"""
        return self.current_state.getState(key)

    def isUp(self, key):
        """Return True if the key is up"""
        return not self.current_state.getState(key)

    def isClicked(self, key):
        """Return True if the key has been clicked"""
        return self.previous_state.getState(key) and (not self.current_state.getState(key))

    def areAnyDown(self):
        """Is any button depressed?"""
        for key in range(len(self.current_state.key_states)):
            if self.isDown(key):
                return True
        return False

    def areAnyClicked(self):
        """Is any button clicked?"""
        for key in range(len(self.current_state.key_states)):
            if self.isClicked(key):
                return True
        return False

    def getClicked(self):
        """Return a list of the keys that are clicked"""
        return [key for key in range(len(self.current_state.key_states)) if self.isClicked(key)]
        
    def update(self, interval):
        """Update the state of the keyboard"""
        keys = pygame.key.get_pressed()
        self.previous_state = self.current_state.getCopy()
        self.current_state.key_states = keys
        #
        events = pygame.event.get((pygame.KEYDOWN))
        #
        self.text_entered = []
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.unicode:
                    self.text_entered.append((K_LETTER, event.unicode))
                else:
                    self.text_entered.append((K_CONTROL, event.key))
        
    def isShiftDown(self):
        """Return True if the shift key is down"""
        return self.isDown(pygame.K_LSHIFT) or self.isDown(pygame.K_RSHIFT) or self.isDown(pygame.K_CAPSLOCK)

    def isControlDown(self):
        """Return True if the control key is down"""
        return self.isDown(pygame.K_LCTRL) or self.isDown(pygame.K_RCTRL)

    def isAltDown(self):
        """Return True if the alt key is down"""
        return self.isDown(pygame.K_LALT) or self.isDown(pygame.K_RALT)

    def getTextEntered(self):
        """Return any text entered since the last call"""
        return self.text_entered
            
class MouseState(object):
    """A structure that contains the states of our mouse buttons."""
    def __init__(self):
        #Stores the pressed value of the left mouse button.
        self.left_pressed = False

        #Stores the pressed value of the middle mouse button.
        self.middle_pressed = False

        #Stores the pressed value of the right mouse button.
        self.right_pressed = False

        #Stores the pressed value of the wheel up button.
        self.wheel_up_pressed = False

        #Stores the pressed value of the wheel down button.
        self.wheel_down_pressed = False

        #The location of the mouse pointer on the screen.
        self.mouse_pos = pymunk.Vec2d()

    def getCopy(self):
        """Return a copy of this state"""
        ms = MouseState()
        ms.left_pressed = self.left_pressed
        ms.middle_pressed = self.middle_pressed
        ms.right_pressed = self.right_pressed
        ms.wheel_up_pressed = self.wheel_up_pressed
        ms.wheel_down_pressed = self.wheel_down_pressed
        ms.mouse_pos = self.mouse_pos
        return ms

    def getState(self, StateType):
        """Return True if the specified button is pressed"""
        if(StateType == M_LEFT):
            #Checking left mouse button
            return self.left_pressed
        elif(StateType == M_MIDDLE):
            #Checking middle mouse button
            return self.middle_pressed
        elif(StateType == M_RIGHT):
            #Checking right mouse button
            return self.right_pressed
        elif(StateType == M_WHEEL_UP):
            #Checking wheel up mouse button
            return self.wheel_up_pressed
        elif(StateType == M_WHEEL_DOWN):
            #Checking wheel down mouse button
            return self.wheel_down_pressed
        
    def setState(self, StateType, state):
        """Set the state of a specific key"""
        if(StateType == M_LEFT):
            #Checking left mouse button
            self.left_pressed = state
        elif(StateType == M_MIDDLE):
            #Checking middle mouse button
            self.middle_pressed = state
        elif(StateType == M_RIGHT):
            #Checking right mouse button
            self.right_pressed = state
        elif(StateType == M_WHEEL_UP):
            #Checking wheel up mouse button
            self.wheel_up_pressed = state
        elif(StateType == M_WHEEL_DOWN):
            #Checking wheel down mouse button
            self.wheel_down_pressed = state
        
        
class Mouse(object):
    """Represents the state of the mouse"""
    
    def __init__(self, engine):
        """Initialise the mouse"""
        super(Mouse, self).__init__()
        self.current_mouse_state = MouseState()
        self.previous_mouse_state = MouseState()
        self.engine = engine
        self._clicks = {}
        self._actors_under_mouse = None
        self._button_lookup = {1: 'left_pressed', 2: 'middle_pressed', 3: 'right_pressed', 4:'wheel_up_pressed', 5: 'wheel_down_pressed'}
        self._wheel_buttons = set([4,5])

    def isDown(self, MouseStateType):
        """Return True if the mouse button is down"""
        return self.current_mouse_state.getState(MouseStateType)

    def isUp(self, MouseStateType):
        """Return True if the mouse button is up"""
        return not self.current_mouse_state.getState(MouseStateType)

    def isClicked(self, MouseStateType):
        """Return True if the mouse button is pressed"""
        return MouseStateType in self._clicks or (self.previous_mouse_state.getState(MouseStateType) and (not self.current_mouse_state.getState(MouseStateType)))

    def clearClick(self, MouseStateType):
        """Clear a click event"""
        self.previous_mouse_state.setState(MouseStateType, False)

    def update(self, interval):
        """Update our mouse states"""
        self.previous_mouse_state = self.current_mouse_state.getCopy()
        events = pygame.event.get((pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP))
        mouse_set = False
        ups, downs, self._clicks, self._actors_under_mouse = {}, {}, {}, None
        #
        for event in events:
            if event.type == pygame.QUIT:
                self.engine.stop()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                button = event.dict['button']
                setattr(self.current_mouse_state, self._button_lookup[button], True)
                downs[button] = True
                if button in self._wheel_buttons:
                    mouse_set = True
            elif event.type == pygame.MOUSEBUTTONUP:
                button = event.dict['button']
                setattr(self.current_mouse_state, self._button_lookup[button], False)
                ups[button] = True
                mouse_set = True
        #
        # Check for clicks that occured during the frame
        for button in (1,2,3,4,5):
            if downs.get(button) and ups.get(button):
                self._clicks[button] = True
        #
        # Clear wheel if not moving
        if not mouse_set:
            self.current_mouse_state.wheel_up_pressed = False
            self.current_mouse_state.wheel_down_pressed = False
        
    def getScreenPos(self):
        """Return the pixel location relative to the screen and camera"""
        absolute = pymunk.Vec2d(*pygame.mouse.get_pos())/self.engine.getRenderer().getCamera().zoom
        x, y, _, _ = self.engine.getRenderer().getCamera().getSpatial()
        return absolute+pymunk.Vec2d(x, y)

    def getScreenPoint(self):
        """Return the location of the mouse relative to the screen as a point"""
        return geometry.Point(*self.getScreenPos())

    def getStaticScreenPos(self):
        """Return the pixel location relative to the screen and NOT camera"""
        return pymunk.Vec2d(*pygame.mouse.get_pos())/self.engine.getRenderer().getCamera().zoom

    def getActorEvents(self, world, layers=None, layer_order=None):
        """Return the type of events for each actor that we have hit
        
        The optional parameter layers can be a list of layers that we are interested in. Only
        actors on the given layers will be returned.
        
        """
        actors = self.getActorsUnderMouse(world)
        #
        # Get list of applying events
        events = []
        if self.isClicked(M_LEFT):
            events.append('left-click')
        elif self.isDown(M_LEFT):
            events.append('left-mouse-down')
        #
        if self.isClicked(M_RIGHT):
            events.append('right-click')
        elif self.isDown(M_RIGHT):
            events.append('right-mouse-down')
        #
        if self.isClicked(M_WHEEL_UP):
            events.append('wheel-up-click')
        if self.isClicked(M_WHEEL_DOWN):
            events.append('wheel-down-click')
        #
        # Sorting and filtering of the events
        if layer_order is None:
            layer_order = {}
        #
        all = []
        for actor in actors:
            if layers is None or actor.layer in layers:
                for event in events:
                    all.append((layer_order.get(actor.layer), (event, actor)))
        #
        all.sort()
        all.reverse()
        #
        return [e for _, e in all]

    def getActorsUnderMouse(self, world):
        """Return all the actors that the mouse is over"""
        if self._actors_under_mouse is None:
            x, y = self.getScreenPos()
            sx, sy = self.getStaticScreenPos()
            r = self.engine.getRenderer()
            try:
                actors_camera = set([a for a in world.findActorsAt(x, y) if not r.getLayer(a.layer).static])
                actors_static = set([a for a in world.findActorsAt(sx, sy) if r.getLayer(a.layer).static])
            except render.UnknownLayer:
                raise render.UnknownLayer('Layer "%s" not found for actor %s' % (a.layer, a.getNiceName()))
            #
            self._actors_under_mouse = actor.ActorCollection(list(actors_static) + list(actors_camera))
        #
        return self._actors_under_mouse
        
        
