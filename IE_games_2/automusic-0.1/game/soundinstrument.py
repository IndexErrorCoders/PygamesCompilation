"""Some classes for wrapping particular instruments"""

import serge.sound
import serge.common


class Instrument(object):
    """Represents a particular instrument"""

    def __init__(self, name, description, notes, cells):
        """Initialise the instrument"""
        self.name = name
        self.description = description
        self.notes = notes
        self.cells = cells
        self.volume = 0.2

    def playCell(self, (cx, cy)):
        """Play the sound for a cell"""
        try:
            note = self.cells[(cx, cy)]
        except KeyError:
            return
        sound_name = self.notes[note]
        sound = serge.sound.Sounds.getItem(sound_name)
        sound.set_volume(self.volume)
        sound.play()

    @classmethod
    def getFromModule(cls, module):
        """Return a new instrument from a module"""
        log = serge.common.getLogger(module.name)
        #
        # Register the sounds
        serge.sound.Sounds.setPath(module.__path__[0])
        for name, filename in list(module.notes.iteritems()):
            sound_name = '%s-%s' % (module.name, name)
            serge.sound.Sounds.registerItem(sound_name, filename)
            module.notes[name] = sound_name
            log.debug('Registered sound %s from %s' % (sound_name, filename))
        #
        # Create the instrument
        obj = cls(module.name, module.description, module.notes, module.cells)
        return obj

