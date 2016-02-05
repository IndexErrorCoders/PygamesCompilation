import pygame, os
import kezmenu

from quantum import Quantum
from tutorial import Tutorial
from credits import Credits
from scores import Highscore

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sounds disabled'

# Function to create resources from chimp tutorial.
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image #, image.get_rect()
    
def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound
    
def load_music(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        music = pygame.mixer.music.load(fullname)
    except pygame.error, message:
        print 'Cannot load music:', fullname
        raise SystemExit, message
    return music
    
def load_font(name, size=12):
    fullname = os.path.join('data', name)
    try:
        font = pygame.font.Font(fullname, size)
    except pygame.error, message:
        print 'Cannot load font:', fullname
        raise SystemExit, message
    return font

def toggle_sound(option):
    if option == 'on':
        pygame.mixer.pause()
        option = 'off'
    elif option == 'off':
        pygame.mixer.unpause()
        option = 'on'
    
    # Main class
class Menu(object):
    running = True
    def main(self, screen):
        pygame.mixer.init()
        clock = pygame.time.Clock()
        background = load_image('menu_background.png')
        music = load_sound('music_credits.ogg')
        menu = kezmenu.KezMenu(
            ['Engage', lambda: Quantum().mainLoop(40)],
            ['Enlighten', lambda: Tutorial().mainLoop(40)],
            ['Archive', lambda: Highscore().mainLoop(40)],
            ['Collaborating Minds', lambda: Credits().mainLoop(40)],
            ['Abort', lambda: setattr(self, 'running', False)],
        )
        menu.x = 10
        menu.y = 10
        menu.enableEffect('raise-col-padding-on-focus', enlarge_time=0.1)
        menu.color = (0, 0, 255)
        menu.focus_color = (174, 23, 92)
        menu.font = load_font('adelle.ttf', 20)
        
        music.play(-1)
            
        while self.running:
            menu.update(pygame.event.get(), clock.tick(30)/1000.)
            screen.blit(background, (0, 0))
            menu.draw(screen)
            pygame.display.flip()
            
if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()
    icon = pygame.Surface((32, 32))
    rawicon = pygame.image.load(os.path.join('data', 'icon.bmp'))
    for i in range(0, 32):
        for j in range (0, 32):
            icon.set_at(((i, j)), rawicon.get_at((i, j)))
    pygame.display.set_icon(icon)
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('python: PULSAR', 'Pulsar')
    Menu().main(screen)