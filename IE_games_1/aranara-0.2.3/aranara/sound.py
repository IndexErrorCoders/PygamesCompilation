"""Sounds for the game"""

import pyglet
import settings

import engine


class Sounds(object):
    """Holds all the sounds"""


class _Music(object):
    """Holds all the music"""


Player = pyglet.media.Player()
Music = _Music()


def initSound(options):
    """Initialise the sound"""
    Sounds.click = pyglet.resource.media('54405__korgms2000b__button-click.wav', streaming=False)
    Sounds.click_forward = pyglet.resource.media('188388__wubitog__mid-high-tone-button-click.wav', streaming=False)
    Sounds.click_backward = pyglet.resource.media('188388__wubitog__mid-high-tone-button-click-low.wav', streaming=False)
    Sounds.click_accept = pyglet.resource.media('188388__wubitog__mid-high-tone-button-click-high.wav', streaming=False)
    Sounds.drop = pyglet.resource.media('96128__bmaczero__contact2.wav', streaming=False)
    Sounds.door = pyglet.resource.media('176146__swagmuffinplus__sliding-doors.wav', streaming=False)

    Sounds.collect = pyglet.resource.media('120502__lth-stp__bell7.wav', streaming=False)
    Sounds.collect_bad = pyglet.resource.media('120502__lth-stp__bell7-low.wav', streaming=False)

    Sounds.end_of_level = pyglet.resource.media('178643__zabuhailo__bronzebell4.wav', streaming=False)

    Music.lunar_t = pyglet.resource.media('Spuntic_-_10_-_Lunar_Trees.mp3', streaming=True)
    Music.lunar = pyglet.media.Player()
    Music.lunar.queue(Music.lunar_t)

    Music.crystal_t = pyglet.resource.media('Spuntic_-_08_-_Crystal_Visions.mp3', streaming=True)
    Music.crystal = pyglet.media.Player()
    Music.crystal.queue(Music.crystal_t)

    Music.spiritual_t = pyglet.resource.media('Spuntic_-_02_-_Spiritual_Dreams.mp3', streaming=True)
    Music.spiritual = pyglet.media.Player()
    Music.spiritual.queue(Music.spiritual_t)

    Music.sinister_t = pyglet.resource.media('Tab__Anitek_-_Sinister_Psyche.mp3', streaming=True)
    Music.sinister = pyglet.media.Player()
    Music.sinister.queue(Music.sinister_t)
