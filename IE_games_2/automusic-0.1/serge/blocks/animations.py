"""Classes to help animating actors"""


import fnmatch
import math

import serge.actor
import serge.engine
import serge.serialize
import serge.registry
import serge.sound
import serge.blocks.effects


class AnimationExists(Exception):
    """An animation already exists with the same name"""


class AnimationNotFound(Exception):
    """The animation was not found"""


class NotPaused(Exception):
    """Tried to start when an animation was not paused"""


class AlreadyPaused(Exception):
    """Tried to pause when an animation was already paused"""


class AnimatedActor(serge.actor.Actor):
    """Implements an actor that can have animations applying to it"""

    def __init__(self, tag, name):
        """Initialise the actor"""
        super(AnimatedActor, self).__init__(tag, name)
        #
        self.animations = {}
        self._paused = False

    def addAnimation(self, animation, name):
        """Add an animation to this actor"""
        if name in self.animations:
            raise AnimationExists('An animation named "%s" already exists for this actor (%s)' % (
                name, self.getNiceName()
            ))
        self.animations[name] = animation
        animation.setActor(self)
        animation.setName(name)
        return animation

    def addRegisteredAnimation(self, name):
        """Add an animation from the animation registry"""
        return self.addAnimation(Animations.getItem(name), name)

    def addRegisteredAnimations(self, names):
        """Add a number of animations from the animation registry"""
        for name in names:
            self.addRegisteredAnimation(name)

    def removeAnimation(self, name):
        """Remove a named animation"""
        try:
            del(self.animations[name])
        except KeyError:
            raise AnimationNotFound('No animation called "%s" found for actor %s' % (
                name, self.getNiceName()
            ))

    def removeAnimations(self):
        """Remove all the animations"""
        self.animations.clear()

    def removeAnimationsMatching(self, pattern):
        """Remove all animations matching a matching pattern"""
        for name in self.animations.keys():
            if fnmatch.fnmatch(name, pattern):
                self.removeAnimation(name)

    def getAnimation(self, name):
        """Return the named animation"""
        try:
            return self.animations[name]
        except KeyError:
            raise AnimationNotFound('No animation called "%s" found for actor %s' % (
                name, self.getNiceName()
            ))

    def getAnimations(self):
        """Return all the animations"""
        return self.animations.values()

    def pauseAnimations(self, safe=False):
        """Pause all animations"""
        if not safe and self._paused:
            raise AlreadyPaused('Animations for %s are already paused' % self.getNiceName())
        self._paused = True

    def unpauseAnimations(self, safe=False):
        """Start all animations"""
        if not safe and not self._paused:
            raise NotPaused('Animations for %s are not paused' % self.getNiceName())
        self._paused = False

    def animationsPaused(self):
        """Return True if our animations are paused"""
        return self._paused

    def restartAnimations(self):
        """Restart all animations"""
        self._paused = False
        for animation in self.getAnimations():
            animation.restart()

    def completeAnimations(self):
        """Complete all animations"""
        self._paused = True
        for animation in self.getAnimations():
            animation.finish()
            animation.update()

    def updateActor(self, interval, world):
        """Update the actor"""
        super(AnimatedActor, self).updateActor(interval, world)
        #
        if not self._paused:
            for animation in self.animations.values():
                animation.updateActor(interval, world)


class Animation(serge.blocks.effects.Effect):
    """The basic animation class"""

    my_properties = (
        serge.serialize.F('duration', 0, 'the length of time the animation runs for in one direction'),
    )

    def __init__(self, duration=1000, done=None, loop=False, paused=False):
        """Initialise the animation"""
        self.actor = None
        self.duration = duration
        super(Animation, self).__init__(done=done, persistent=True)
        #
        self.init()
        self.paused = paused
        self.loop = loop

    def setActor(self, actor):
        """Set our actor"""
        self.actor = actor

    def setName(self, name):
        """Set our name"""
        self.name = name

    def init(self):
        """Initialise the properties"""
        super(Animation, self).init()
        self.name = None
        self.start = 0
        self.end = self.duration
        self.current = 0
        self.iteration = 0
        self.fraction = 0.0
        self.complete = False
        self.direction = 1
        self.interval = 0
        self._pause_next_cycle = False

    def unpause(self):
        """Un-pause the animation"""
        super(Animation, self).unpause()
        self._pause_next_cycle = False

    def restart(self):
        """Restart the animation"""
        self.init()
        self.update()

    def updateActor(self, interval, world):
        """Update the animation effect"""
        super(Animation, self).updateActor(interval, world)
        #
        # Do not advance time if we are paused
        if self.paused:
            return
        #
        self.current += self.direction * interval
        self.iteration += 1
        self.interval = interval
        #
        # Watch for bouncing
        if self.loop:
            if self.direction == 1 and self.current >= self.end:
                self.current = self.duration - (self.current - self.duration)
                self.direction *= -1
            elif self.direction == -1 and self.current <= 0:
                if self._pause_next_cycle:
                    self.current = 0
                    self.pause()
                else:
                    self.current = -self.current
                self.direction *= -1
        #
        # Map back into proper space
        # TODO: a proper implementation should also account for going through more than one iteration
        self.current = min(self.duration, max(0, self.current))
        self.fraction = min(1.0, float(self.current) / self.duration)
        #
        self.update()
        #
        if self.fraction == 1.0:
            self.finish()

    def finish(self):
        """Finish the effect"""
        self.current = self.end
        self.fraction = 1.0
        self._effectComplete(None)
        self.complete = True

    def pauseAtNextCycle(self):
        """Set the animation to pause at the next time it renews a cycle"""
        self._pause_next_cycle = True

    def update(self):
        """The main method implementing the animation effect

        This is the method you should implement

        """


class AnimationRegistry(serge.registry.GeneralStore):
    """A place to register animations so they can be easily re-used"""

    def _registerItem(self, name, item):
        """Register the animation"""
        #
        # Remember the settings used to create the sound
        self.raw_items.append([name, item])
        self.items[name] = item
        return None

    def getItem(self, name):
        """Return an animation

        We need to deepcopy the animation to avoid returning the same one
        each time.

        """
        item = super(AnimationRegistry, self).getItem(name)
        return item.copy()


# Singleton animation registry
Animations = AnimationRegistry()

#
# Now we have some specific examples of useful animations


class PulsedVisibility(Animation):
    """An animation that turns an actor on and off with visibility"""

    my_properties = (
        serge.serialize.F('on_fraction', 0.5, 'the fraction of the time to stay visibible for'),
    )

    def __init__(self, duration, on_fraction=0.5):
        """Initialise the animation"""
        super(PulsedVisibility, self).__init__(duration=duration, loop=True)
        self.on_fraction = on_fraction

    def update(self):
        """Update the animation"""
        self.actor.visible = self.fraction <= self.on_fraction


class ColourCycle(Animation):
    """Animate the colour property of an object between a beginning and end"""

    def __init__(self, obj, start_colour, end_colour, duration,
                 attribute='colour', loop=False, done=None):
        """Initialise the animation"""
        super(ColourCycle, self).__init__(duration, loop=loop, done=done)
        #
        self.obj = obj
        self.start_colour = start_colour
        self.end_colour = end_colour
        self.attribute = attribute

    def update(self):
        """Update the colour of the object"""
        #
        # Work out the values for each element of the colour
        colours = []
        for x, y in zip(self.start_colour, self.end_colour):
            colours.append(float(x + (y - x) * self.fraction))
        #
        self.setColour(tuple(colours))

    def setColour(self, colour):
        """Set the colour"""
        setattr(self.obj, self.attribute, colour)


class ColourText(ColourCycle):
    """Animate the colour of a text object by calling its setColour method"""

    def setColour(self, colour):
        """Set the colour"""
        self.obj.setColour(colour)
        if len(colour) == 4:
            self.obj.setAlpha(float(colour[-1]) / 255)


class MoveWithVelocity(Animation):
    """Animate the motion of an actor with a constant velocity"""

    my_properties = (
        serge.serialize.F('vx', 0.0, 'the x velocity to move with'),
        serge.serialize.F('vy', 0.0, 'the y velocity to move with'),
    )

    def __init__(self, (vx, vy), loop=False, done=None):
        """Initialise the animation"""
        super(MoveWithVelocity, self).__init__(duration=1000, loop=loop, done=done)
        #
        self.vx = vx
        self.vy = vy

    def update(self):
        """Update the actor"""
        self.actor.move(self.interval / 1000.0 * self.vx, self.interval / 1000.0 * self.vy)


class MouseOverAnimation(Animation):
    """A base class to use for animations that can be activated by mouse over

    Animations extending this class can set mouse_over_only to True and then
    the animation will run only when the mouse is over the actor. When the
    mouse moves out then the animation will run to the beginning of the
    cycle and then stop.

    """

    my_properties = (
        serge.serialize.B('mouse_over_only', False, 'whether we only animate on mouse over'),
    )

    def __init__(self, duration, mouse_over_only, loop=False, done=None, paused=False):
        """Initialise the animation"""
        super(MouseOverAnimation, self).__init__(duration, loop=loop, done=done, paused=paused)
        #
        self.mouse_over_only = mouse_over_only

    def init(self):
        """Initialise the animation"""
        super(MouseOverAnimation, self).init()
        self.mouse = serge.engine.CurrentEngine().getMouse()

    def updateActor(self, interval, world):
        """Update the animation"""
        #
        # Check if we should re-activate
        if self.mouse_over_only:
            inside = self.mouse.getScreenPoint().isInside(self.actor)
            if inside:
                if self.paused:
                    self.unpause()
            else:
                self.pauseAtNextCycle()
        #
        super(MouseOverAnimation, self).updateActor(interval, world)


class PulseZoom(MouseOverAnimation):
    """Cycle the zoom of an actor between a high and low value"""

    my_properties = (
        serge.serialize.F('start_zoom', False, 'the initial zoom value'),
        serge.serialize.F('end_zoom', False, 'the final zoom value'),
    )

    def __init__(self, start_zoom, end_zoom, duration,
                 loop=False, done=None, mouse_over_only=False, paused=False):
        """Initialise the animation"""
        super(PulseZoom, self).__init__(
            duration, mouse_over_only=mouse_over_only, loop=loop, done=done, paused=paused)
        #
        self.start_zoom = start_zoom
        self.end_zoom = end_zoom

    def update(self):
        """Update the zoom of the object"""
        super(PulseZoom, self).update()
        if not self.paused:
            zoom = float(self.fraction * (self.end_zoom - self.start_zoom) + self.start_zoom)
            self.actor.setZoom(zoom)


class PulseRotate(MouseOverAnimation):
    """Cycle the rotation of an actor between a high and low value

    The rotation limits are set as the min and max angle. The actual
    start point of the animation is half way between the two. This
    means that if you stop it on a cycle it will return to the mid point.

    """

    my_properties = (
        serge.serialize.F('min_angle', False, 'the low value of the angle'),
        serge.serialize.F('max_angle', False, 'the high value of the angle'),
    )

    def __init__(self, min_angle, max_angle, duration,
                 loop=False, done=None, mouse_over_only=False, paused=False):
        """Initialise the animation"""
        super(PulseRotate, self).__init__(
            duration, mouse_over_only=mouse_over_only, loop=loop, done=done, paused=paused)
        #
        self.min_angle = min_angle
        self.max_angle = max_angle

    def update(self):
        """Update the angle of the object"""
        super(PulseRotate, self).update()
        if not self.paused:
            time_fraction = self.fraction if self.direction == 1 else 2.0 - self.fraction
            effective_fraction = math.sin(time_fraction * math.pi) / 2 + 0.5
            angle = float(effective_fraction * (self.max_angle - self.min_angle) + self.min_angle)
            self.actor.setAngle(angle)


class MouseOverSound(Animation):
    """Plays a sound when mousing over something"""

    my_properties = (
        serge.serialize.S('sound', '', 'the sound to play'),
        serge.serialize.B('over', False, 'whether the mouse is over us'),
    )

    def __init__(self, sound):
        """Initialise the animation"""
        super(MouseOverSound, self).__init__(duration=1)
        #
        self.sound = sound

    def init(self):
        """Initialise the animation"""
        super(MouseOverSound, self).init()
        self.mouse = serge.engine.CurrentEngine().getMouse()
        self.over = False

    def update(self):
        """Update the animation"""
        if self.mouse.getScreenPoint().isInside(self.actor):
            if not self.over:
                serge.sound.Sounds.play(self.sound)
                self.over = True
        else:
            self.over = False