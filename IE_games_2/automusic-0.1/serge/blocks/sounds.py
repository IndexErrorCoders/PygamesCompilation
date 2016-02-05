"""Useful blocks for sounds"""

import math
import random

import serge.sound
import serge.actor


class NoListener(Exception): """Positional sound enabled but there is no listener set"""


class SoundTexture(serge.actor.Actor):
    """An actor that manages a number of sounds to create a texture
    
    The actor can control sounds that are produced either ambiently (everywhere)
    or at specific locations. For the sounds at specific locations the sounds
    will get louder as the listener gets closer to them.
    
    """

    def __init__(self, tag, name, damping=None):
        """Initialise the SoundTexture"""
        super(SoundTexture, self).__init__(tag, name)
        #
        self.sounds = []
        self.random_sounds = []
        self.listener = None
        self._master_volume = 1.0
        self._listener_required = False
        self.damping = damping
        self._playing = False
        
    def setListener(self, listener):
        """Set the listener for the sounds
        
        The listener is an actor and the sounds play at a volume determined
        by the location of the listener relative to each sound.
        
        :param listener: an actor
        
        """
        self.listener = listener
        
    def getListener(self):
        """Return the listener"""
        return self.listener
        
    def addAmbientSound(self, sound):
        """Add an ambient sound to the texture
        
        An ambient sound plays at the same volume no matter where the listener
        is. Ambient sounds still get paused with the other sounds.
        
        :param sound: the serge sound object that should be played
        
        """
        self.sounds.append(AmbientSound(sound))

    def addRandomSound(self, sound, probability):
        """Add a random sound to the texture
        
        A random sound plays with a likelihood of probability/second. 
        
        :param sound: the serge sound object that should be played
        :param probability: the probability that the sound will play in a given second
        
        """
        self.random_sounds.append(ProbabalisticSound(sound, probability))

    def addPositionalSound(self, sound):
        """Add a positional sound to the texture
        
        A position sound plays at one or more locations in space and its volume is dependent
        on the location of the listener.

        :param sound: the sound object that should be played. It should inherit from AmbientSound
        
        """
        self.sounds.append(sound)
        self._listener_required = True
        
    def getSounds(self):
        """Return all the sounds that we are controlling"""
        return self.sounds
   
    def set_volume(self, volume):
        """Set the master volume
        
        This affects the volume of all sounds. The target volume for a sound is multiplied
        by this master.
        
        :param volume: master volume setting (0=silent, 1=full volume)
        
        """
        self._master_volume = volume
        for sound in self.getSounds():
            sound.set_volume(volume)
       
    def get_volume(self):
        """Return the master value setting"""
        return self._master_volume
     
    def play(self, loops=0):
        """Play the sounds
        
        :param loops: number of times to loop the sounds (0=never, -1=for ever)
        
        """
        for sound in self.getSounds():
            sound.play(loops)
        self._playing = True
        
    def pause(self):
        """Pause the sounds"""
        for sound in self.getSounds():
            sound.pause() 
        self._playing = False
                       
    def stop(self):
        """Stop the sounds"""
        for sound in self.getSounds():
            sound.stop() 
        self._playing = False
            
    def updateActor(self, interval, world):
        """Update the actor"""
        super(SoundTexture, self).updateActor(interval, world)
        #
        # Update the volume of all sounds
        if self.listener:
            for sound in self.sounds:
                #
                # Update the sound volume
                current_volume = sound.get_volume()
                target_volume = sound.get_scaled_volume((self.listener.x, self.listener.y))
                #
                # Damp changes in the sound volume
                if self.damping is None:
                    new_volume = target_volume*self._master_volume
                else:
                    new_volume = max(0.0, min(1.0, interval/1000.0*self.damping)*
                                    (target_volume - current_volume) + current_volume)*self._master_volume
                sound.set_volume(new_volume)
        elif self._listener_required:
            raise NoListener('A listener has not been set for this texture (%s)' % self.getNiceName())
        #
        # Play any random sounds
        if self._playing:
            for sound in self.random_sounds:
                sound.try_to_play(interval)


class ProbabalisticSound(serge.sound.SoundItem):
    """A sound that plays with a certain probability"""

    def __init__(self, sound, probability):
        """Initialise the ProbabalisticSound"""
        super(ProbabalisticSound, self).__init__(sound=sound)
        self.probability = probability
        
    def try_to_play(self, interval):
        """Try to play the sound"""
        if random.random() < self.probability * interval/1000.0:
            self.play()
            
            

class AmbientSound(serge.sound.SoundItem):
    """A sound located everywhere in space"""
    
    def __init__(self, sound):
        """Initialise the sound"""
        super(AmbientSound, self).__init__(sound=sound)
        
    def get_scaled_volume(self, listener_position):
        """Return the sound volume according to the listener position"""
        return 1.0
               
        
class LocationalSound(AmbientSound):
    """A sound that is located somewhere in space"""
    
    def __init__(self, sound, location, dropoff):
        """Initialise the sound"""
        super(LocationalSound, self).__init__(sound)
        #
        self.location = location
        self.dropoff = dropoff
        
    def get_scaled_volume(self, listener_position):
        """Update the sound volume according to the listener position"""
        dist = math.sqrt((listener_position[0]-self.location[0])**2 +(listener_position[1]-self.location[1])**2)
        return max(0.0, 1.0-dist/self.dropoff)
       

class LocationalSounds(AmbientSound):
    """A series of sounds that are located at a number of places in space but generate only a single sound"""
    
    def __init__(self, sound, locations, dropoff):
        """Initialise the sound"""
        super(LocationalSounds, self).__init__(sound)
        #
        self.locations = locations
        self.dropoff = dropoff
        
    def get_scaled_volume(self, listener_position):
        """Update the sound volume according to the listener position"""
        total = 0.0
        for location in self.locations:
            dist = math.sqrt((listener_position[0]-location[0])**2 +(listener_position[1]-location[1])**2)
            total += max(0.0, 1.0-dist/self.dropoff)
        return min(1.0, total)
       
       
class ActorsWithTagSound(AmbientSound):
    """A series of sounds that are located on actors who are in the world and have a certain tag"""
    
    def __init__(self, sound, world, tag, dropoff):
        """Initialise the sound"""
        super(ActorsWithTagSound, self).__init__(sound)
        #
        self.world = world
        self.tag = tag
        self.dropoff = dropoff
        
    def get_scaled_volume(self, listener_position):
        """Update the sound volume according to the listener position"""
        total = 0.0
        for actor in self.world.findActorsByTag(self.tag):
            dist = math.sqrt((listener_position[0]-actor.x)**2 +(listener_position[1]-actor.y)**2)
            total += max(0.0, 1.0-dist/self.dropoff)
        return min(1.0, total)   
 
 
class RectangularRegionSound(AmbientSound):
    """A sound that is located in a rectangular region
    
    Inside the region the volume is full and outside the region the volume is 
    zero.
    
    """
    
    def __init__(self, sound, region):
        """Initialise the sound"""
        super(RectangularRegionSound, self).__init__(sound)
        #
        self.location = serge.geometry.Rectangle(*region)
        
    def get_scaled_volume(self, listener_position):
        """Update the sound volume according to the listener position"""
        p = serge.geometry.Point(*listener_position)
        return 1.0 if p.isInside(self.location) else 0.0
        
         
           
