"""The sound classes"""

import os

import pygame

import common
import serialize
import registry 
import events

#
# Initialise the pygame sound subsystem
pygame.mixer.init()
pygame.mixer.set_num_channels(common.NUM_AUDIO_CHANNELS)

class UnknownSound(Exception): """The sound was not found"""
class BadSound(Exception): """Could not load sound from"""


class AudioRegistry(registry.GeneralStore, common.EventAware):
    """Registry for audio"""
    
    def __init__(self):
        """Initialise the registry"""
        super(AudioRegistry, self).__init__()
        self._paused = False
        self.initEvents()
        self.playing = None

    def play(self, name, loops=0):
        """Play a sound
        
        :param name: the name of the sound to play
        :param loops: the number of times to loop the sound (0=do not loop, -1=loop forever)
        
        """
        self.getItem(name).play(loops)
        self.playing = self.getItem(name)
   
    def pause(self):
        """Pause all sounds"""
        self._paused = True
        if self.playing:
            self.playing.pause()

    def unpause(self):
        """Unpause all sounds"""
        self._paused = False
        if self.playing:
            self.playing.unpause()
    
    def toggle(self):
        """Toggle whether music or sound is playing or not"""
        if self.isPaused():
            self.unpause()
        else:
            self.pause()
        
    def isPaused(self):
        """Return True if we are paused"""
        return self._paused

    def update(self, interval):
        """Update the registry looking for events
        
        The method is called automatically by the engine.
        
        """

    def isPlaying(self):
        """Return True if we are playing"""
                    
        
class Store(AudioRegistry):
    """Stores sounds"""
    
    def _registerItem(self, name, path):
        """Register the sound"""
        #
        # Load the sound
        try:
            sound = SoundItem(self._resolveFilename(path))
        except Exception, err:
            raise BadSound('Failed to load sound from "%s": %s' % (path, err))
        
        #
        # Remember the settings used to create the sound
        self.raw_items.append([name, path])
        self.items[name] = sound
        return sound
    
    def isPlaying(self):
        """Return True if we are playing"""
        return pygame.mixer.get_busy()
        
            
class MusicStore(AudioRegistry):
    """Stores music"""

    def __init__(self):
        """Initialise the store"""
        super(MusicStore, self).__init__()
        self._last_playing = None
        self.playlist = None
        
    def _registerItem(self, name, path):
        """Register the music"""
        if not os.path.isfile(self._resolveFilename(path)):
            raise BadSound('No music file "%s"' % self._resolveFilename(path))
        #
        # Remember the settings used to create the music
        self.raw_items.append([name, path])
        self.items[name] = MusicItem(self._resolveFilename(path))
        return self.items[name]

    def update(self, interval):
        """Update the registry looking for events
        
        The method is called automatically by the engine.
        
        """
        super(MusicStore, self).update(interval)
        if not self.isPlaying() and self._last_playing:
            self.processEvent((events.E_TRACK_ENDED, self))
            #
            # If playing a playlist then move to the next one
            if self.playing and not self._paused and self.playlist:
                new = self.playlist.pop(0)
                self.play(new)
                self.playlist.append(new)
        #
        self._last_playing = self.isPlaying()

    def isPlaying(self):
        """Return True if we are playing"""
        return pygame.mixer.music.get_busy()

    def isPlayingSong(self, name):
        """Return True if the named song is playing
        
        :param name: the name of the music item
        
        """
        return self.playing == self.getItem(name)
    
    def setPlaylist(self, item_list):
        """Set a playlist"""
        current = item_list.pop(0)
        item_list.append(current)
        self.play(current)
        self.playlist = item_list
        
    def fadeout(self, time):
        """Fadeout the currently playing track
        
        :param time: the time over which the music fades out in seconds (0=immediate)
        
        """
        pygame.mixer.music.fadeout(int(time))
        self.playing = False

    def setVolume(self, volume):
        """Set the volume
        
        :param volume: the volume of the music (0=silent, 1=full volume)
        
        """
        pygame.mixer.music.set_volume(volume)
        
    def getVolume(self):
        """Returns the volume (0=silent, 1=full volume)"""
        return pygame.mixer.music.get_volume()

           
class MusicItem(object):
    """Represents a music item"""
    
    def __init__(self, path):
        """Initialise the piece of music"""
        self._path = path   
        self._paused = False
    
    def play(self, loops=0):
        """Play the music
        
        :param loops: the number of times to loop the music (0=do not loop, -1=loop forever)
        
        """
        pygame.mixer.music.stop()
        pygame.mixer.music.load(self._path)
        Music.playing = self
        self._paused = False
        if not Music.isPaused():
            pygame.mixer.music.play(loops)
            return True
        else:
            return False
    
    def pause(self):
        """Pause the music"""
        pygame.mixer.music.pause()
        self._paused = True
                
    def unpause(self):
        """Pause the music"""
        if Music.playing == self and self._paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.play()

    def stop(self):
        """Stop the music"""
        pygame.mixer.music.stop()
        Music.playing = None
        self._paused = False
    
    
class SoundItem(object):
    """Represents a sound item
    
    :param path: the path to the sound file
    
    """
    
    def __init__(self, path=None, sound=None):
        """Initialise the sound"""
        if path:
            self._sound = pygame.mixer.Sound(path)
        else:
            self._sound = sound
        self._channel = None
    
    def play(self, loops=0):
        """Play the music
        
        :param loops: the number of times to loop the sound (0=do not loop, -1=loop forever)
        
        """
        if not Sounds.isPaused():
            self._channel = self._sound.play(loops)
            return True
        return False
    
    def pause(self):
        """Pause the sound"""
        self._sound.stop()
        
    def unpause(self):
        """Pause the sound"""
        self._sound.play()

    def stop(self):
        """Stop the sound"""
        self._sound.stop()
        
    def set_volume(self, volume):
        """Set the volume of the sound
        
        :param volume: the volume of the sound (0=silent, 1=full volume)
        
        """
        self._sound.set_volume(volume)
        
    def get_volume(self):
        """Return the volume that the sound is playing at (0=silent, 1=full volume)"""
        return self._sound.get_volume()
        
    def fadeout(self, time):
        """Fadeout the sound
        
        :param time: the time over which the sound fades out in seconds (0=immediate)
        
        """
        self._sound.fadeout(time)

    def isPlaying(self):
        """Return True if the sound is currently playing"""
        if self._channel and self._channel.get_busy():
            return True
        else:
            return False

            
Sounds = Store()
Music = MusicStore()
