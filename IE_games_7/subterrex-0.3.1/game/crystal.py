"""Implements crystals, which are present in the cave and have various properties"""

import pygame
import textwrap

import serge.actor

import climbing
from theme import G, theme
import common 
import textgenerator

class Crystal(serge.actor.Actor):
    """A crystal in the cave"""

    def __init__(self, tag, name):
        """Initialise the Crystal"""
        super(Crystal, self).__init__(tag, name)
        #
        self.setSpriteName('crystal')
        self.setLayerName('actors')
        self.setPhysical(serge.physical.PhysicalConditions(1, force=climbing.G, visual_size=True, update_angle=True))

    def takenByPlayer(self, player, world):
        """The crystal was taken by the player"""
        world.scheduleActorRemoval(self)
        serge.sound.Sounds.play('take-crystal')


class FluorescentCrystal(Crystal):
    """A crystal that amplifies the local light"""
    
    light_factor_name = 'fluorescent-light-factor'
    
    def updateLighting(self, cells, (cx, cy)):
        """Update the lighting map"""
        r = g = b = a = 0
        fr, fg, fb, fa = G(self.light_factor_name)
        #
        # Sample around the current cell to find the maximum light
        for dx in (-1, 0, +1):
            for dy in (-1, 0, +1):
                nx = min(len(cells[0])-1, max(0, cx+dx))
                ny = min(len(cells)-1, max(0, cy+dy))
                nr, ng, nb, na = cells[ny][nx]
                r = max(r, nr)
                g = max(g, ng)
                b = max(b, nb)
                a = max(a, na)
        cells[cy][cx] = min(255,r*fr),min(255, g*fg),min(255, b*fb),min(255, a*fa)#r, g, b, 0
        self.log.debug('Crystal changed light from %s to %s' % ((r,g,b,a), cells[cy][cx]))


class LuminescentCrystal(Crystal):
    """A crystal that generates light"""
            
    def updateLighting(self, cells, (cx, cy)):
        """Update the lighting map"""
        fr, fg, fb, fa = G('luminescent-light-factor')
        #
        # Add some light in there
        nr, ng, nb, na = cells[cy][cx]
        r = max(fr, nr)
        g = max(fg, ng)
        b = max(fb, nb)
        a = max(fa, na)
        cells[cy][cx] = min(255,r),min(255, g),min(255, b),min(255, a)
                

class NamedCrystal(FluorescentCrystal):
    """A crystal that has some history attached to it"""

    light_factor_name = 'named-light-factor'
    
    def __init__(self, tag, name):
        """Initialise the NamedCrystal"""
        super(NamedCrystal, self).__init__(tag, name)
        #
        self.properties = {}
        self.description = '\n'.join(textwrap.wrap(
            NAMES.getRandomSentence('@description@', self.properties),
            G('banner-characters', 'named-crystal')))
        self.name = NAMES.getRandomSentence('@short-jewel-description@', self.properties)
        self.globals = serge.blocks.singletons.Store.getItem('globals')  
        
    def updateLighting(self, cells, (cx, cy)):
        """Update the lighting map"""
        r = g = b = a = 0
        fr, fg, fb, fa = G(self.light_factor_name)
        #
        # Sample around the current cell to find the maximum light
        for dx in (-1, 0, +1):
            for dy in (-1, 0, +1):
                nx = min(len(cells[0])-1, max(0, cx+dx))
                ny = min(len(cells)-1, max(0, cy+dy))
                nr, ng, nb, na = cells[ny][nx]
                r = max(r, nr)
                g = max(g, ng)
                b = max(b, nb)
                a = max(a, na)
        if max(r, g, b) > G('named-light-tolerance'):
            cells[cy][cx] = (fr),(fg),(fb),(fa)
            self.log.debug('Crystal changed light from %s to %s' % ((r,g,b,a), cells[cy][cx]))

    def takenByPlayer(self, player, world):
        """The crystal was taken by the player"""
        super(NamedCrystal, self).takenByPlayer(player, world)
        #
        # Remove any other banner
        if world.getActors().hasActorWithName('crystal-banner'):
            world.removeActor(world.findActorByName('crystal-banner'))
        #
        # Show the name of the crystal
        self.banner = CrystalBanner('banner', 'crystal-banner', self, 'ui-back', 'ui', theme)
        self.banner.moveTo(*G('banner-position', 'named-crystal'))
        world.addActor(self.banner)
        #
        crystal_name = "%(last-name)s's %(jewel)s" % self.properties
        self.globals.history.recordNamedCrystal(crystal_name, self.description, self.globals.last_cave_name)
        
        
class CrystalBanner(serge.actor.MountableActor):
    """A banner to show a named crystal"""

    def __init__(self, tag, name, crystal, background_layer, foreground_layer, theme):
        """Initialise the AchievementBanner"""
        super(CrystalBanner, self).__init__(tag, name)
        G = self.G = theme.getTheme('named-crystal').getProperty
        self.background_layer = background_layer
        self.foreground_layer = foreground_layer 
        self.crystal = crystal
        self.globals = serge.blocks.singletons.Store.getItem('globals')  
                
    def addedToWorld(self, world):
        """Added the banner to the world"""
        super(CrystalBanner, self).addedToWorld(world)
        G = self.G
        self.keyboard = serge.engine.CurrentEngine().getKeyboard()
        self.world = world
        #
        # Create the widgets
        bg = serge.actor.Actor('banner', 'background')
        bg.visual = serge.blocks.visualblocks.Rectangle(G('banner-size'), 
            G('banner-backcolour'))
        bg.setLayerName(self.background_layer)
        self.mountActor(bg, (0, 0))
        #
        self.crystal_name = name = serge.blocks.actors.StringText('banner', 'banner-name', 'Name',
            colour=G('banner-font-colour'), font_size=G('banner-name-size'),
            font_name=G('banner-font-name'), justify='left')
        name.setLayerName(self.foreground_layer)
        self.mountActor(name, G('banner-name-position'))
        #
        self.description = description = serge.blocks.actors.StringText('banner', 'banner-description', 
            'Description of the achievement as it\nis written down.',
            colour=G('banner-font-colour'), font_size=G('banner-description-size'),
            font_name=G('banner-font-name'), justify='left')
        description.setLayerName(self.foreground_layer)
        self.mountActor(description, G('banner-description-position'))
        #
        self.clear = clear = serge.blocks.actors.StringText('banner', 'banner-clear', 
            'Press ENTER to close',
            colour=G('banner-close-font-colour'), font_size=G('banner-close-size'),
            font_name=G('banner-font-name'), justify='left')
        clear.setLayerName(self.foreground_layer)
        clear.linkEvent(serge.events.E_LEFT_CLICK, self.playerRemovesBanner)
        self.mountActor(clear, G('banner-close-position'))
        #
        graphic = serge.actor.Actor('banner', 'banner-graphic')
        graphic.setSpriteName('named-crystal')
        graphic.setLayerName(self.foreground_layer)
        self.mountActor(graphic, G('banner-graphic-position'))
        #
        self.crystal_name.value = self.crystal.name
        self.description.value = self.crystal.description
        #
        self.log.debug('Showing crystal banner')
        self.visible = True
        #
        # Make sure we go away if the level is ending
        self.player = world.findActorByName('player')
        self.player.linkEvent(common.E_PLAYER_DIED, self.clearOut)
        self.player.linkEvent(common.E_CAVE_SOLVED, self.clearOut)
        #
        # Make the banner sound audible
        self.globals.banner_sound.location = (self.player.x, self.player.y)
        
    def updateActor(self, interval, world):
        """Update the actor"""
        super(CrystalBanner, self).updateActor(interval, world)
        #
        if self.keyboard.isClicked(pygame.K_RETURN) or self.keyboard.isClicked(pygame.K_KP_ENTER):
            self.playerRemovesBanner()
            
    def playerRemovesBanner(self, obj=None, arg=None):
        """Player requested us to remove the banner"""
        serge.sound.Sounds.play('ok-crystal')
        self.clearOut(obj, arg)

    def clearOut(self, obj, arg):
        """Clear the banner"""
        self.world.scheduleActorRemoval(self)
        #
        # Make the banner sound inaudible
        self.globals.banner_sound.location = (-10000, -10000)
        

NAMES = textgenerator.TextGenerator()
NAMES.addExamplesFromText(
"""
    colour:  red
    colour:  blue
    colour:  green 
    colour:  yellow
    colour:  purple 
    colour:  black 
    colour:  fuscia 
    #
    jewel:   diamond
    jewel:   ruby
    jewel:   emerald
    jewel:   saphire    
    #
    size: small
    size: tiny
    size: large
    size: giant
    #
    time-span: everlasting
    time-span: temporary
    time-span: nighttime
    time-span: daytime
    time-span: lifelong
    time-span: eternal
    #
    effect: wellness
    effect: charm
    effect: charisma
    effect: intellect
    #
    jewel-item:  @colour@ @jewel@
    jewel-item:  @jewel@
    #
    jewel-description: The @size@ @jewel-item@ of @property@
    jewel-description: The @jewel-item@ of @property@
    short-jewel-description: @jewel-item@
    #
    property: @time-span@ @effect@
    property: @effect@
    #
    reason: was @verb@ by @name@ in @time@
    verb: lost
    verb: placed
    verb: discarded
    verb: mislaid
    verb: dropped
    verb: buried
    verb: discovered
    #
    name: @first-name@ @last-name@
    name: @first-name@ @last-name@ @post-name@
    first-name: Bob
    first-name: Fred
    first-name: Jim
    first-name: Bill
    first-name: Marvin
    first-name: Jill
    first-name: Alice
    first-name: Sheila
    first-name: Lemon
    last-name: Smith
    last-name: Jones
    last-name: Crimson
    last-name: Little
    last-name: Jenson
    last-name: Williams
    post-name: Junior
    post-name: Senior
    post-name: I
    post-name: II
    #
    time: 1900's
    time: 1800's
    time: 1950's
    time: 1960's
    time: 1970's
    time: 1980's
    time: 1990's
    #
    follow-on: @first-name@ went on to @destiny@.
    follow-on: @last-name@ went on to @destiny@.
    follow-on: @first-name@ died in this very cave.
    follow-on: @last-name@ died in this very cave.
    follow-on: @first-name@ died in a @sport@ accident at the age of @death-age@.
    destiny: die from @disease@
    destiny: live to the age of @death-age@
    destiny: become @final-role@
    #
    disease: short pox
    disease: rickets
    disease: intestinal fragrances
    #
    death-age: 45
    death-age: 90
    death-age: 87
    death-age: 125
    #
    final-role: president
    final-role: scoutmaster general
    final-role: a master criminal
    final-role: a knight templar
    #
    sport: caving
    sport: climbing
    sport: diving
    sport: tennis
    sport: tiddly winks
    #
    description: @jewel-description@ @reason@. @follow-on@
    #
"""
)            

if __name__ == '__main__':
    for i in range(20):
        print NAMES.getRandomSentence('@description@')  
