from pygamehelper import *
from pygame import *
from pygame.locals import *
from vec2d import *
from math import e, pi, cos, sin, sqrt
from random import uniform, randrange, choice, randint
import os
from scores import Highscore
import inputbox

def open_file(name):
    fullname = os.path.join('data', name)
    file = open(fullname, 'a')
    return file


def load_font(name, size=12):
    fullname = os.path.join('data', name)
    try:
        font = pygame.font.Font(fullname, size)
    except pygame.error, message:
        print 'Cannot load font:', fullname
        raise SystemExit, message
    return font
    

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

class Charactor:
    def __init__(self):
        self.pos = vec2d(0, 0)
        self.vel = vec2d(0, 0)
        self.acc = vec2d(0, 0)
        
        self.rect = pygame.Rect((self.pos), (5, 5))
        
        self.move = vec2d(0, 0)
        
        self.create_rate = 3000 # create particles every no. milliseconds 
        self.clock = pygame.time.Clock()
        self.tracker = 0
        self.dt = 0
        self.absorbed = False # Whether the player has been absorbed or not
        self.life = 100
        
class Magnet:
    def __init__(self, radius=10):
        self.pos = vec2d(0, 0)
        self.vel = vec2d(3, 0)
        self.vel.rotate(uniform(0, 359))
        self.radius = radius
        self.mass = radius**2
        
        self.side = 0
        self.life = self.radius
        
class Tinie:
    def __init__(self, pos):
        self.pos = vec2d(pos)
        self.vel = vec2d(3, 0)
        
        self.radius = 2
        self.life = 40
        self.side = 0
        self.live = True
        
class Particle:
    def __init__(self, pos):
        self.pos = vec2d(pos)
        self.vel = vec2d(3, 0)
        self.acc = vec2d(0, 0)
        self.life = 40 + randrange(0, 20)
        
class Quantum(PygameHelper):
    def __init__(self):
        self.w, self.h = 800, 600
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))
        
        self.pause = False
        
        self.selected = 0   
        self.right_limit = (self.w/2, self.w)
        self.left_limit = (0, self.w/2)
        
        self.max_vel = 5 # Maximum velocity magnitude
        self.max_acc = 0.5 # Accelaration rate
        self.charactors = [] # Charactor list
        self.magnets = [] # Magnets list
        self.particles = [] # Particles list
        self.tinies = [] # List of tiny non-effective magnets
        self.grav_const = 2.0 # Gravitational constant
        self.grav_radius = 200 # Distance where particles are drawn in. 
        self.create_no = 10 # Initial number of starting particles
        self.radius_list = (3, 5, 10, 20) # list of random radius'to get results from
        
        self.score = 0 # Score of player
        
        self.background = load_image('game_background.png') # Loads the background image
        self.score_font = load_font('adelle.ttf', 16) #  Loads the highscore font up
        
        self.pulA_surf = self.score_font.render('Pulsar A:', True, (0, 47, 113))
        self.pulB_surf = self.score_font.render('Pulsar B:', True, (0, 47, 113))
        self.scoA_surf = self.score_font.render('100%', True, (180, 180, 180)) 
        self.scoB_surf = self.score_font.render('100%', True, (180, 180, 180)) 
        
        # Create two charactor instances        
        for c in range(2):
            c = Charactor()
            self.charactors.append(c)
        
        # Two start positions    
        self.charactors[0].pos = vec2d(self.w/4, self.h*3/4)
        self.charactors[1].pos = vec2d(self.w*3/4, self.h*3/4)
        
        for c in self.charactors:
            c.rect.center = c.pos
        
        # Create list of magnets
        for m in range(2):
            m = Magnet(10)
            m.pos = vec2d(uniform(m.radius, self.w/2 - m.radius), uniform(m.radius, self.h/2 - m.radius))
            self.magnets.append(m)
        for m in range(2):
            m = Magnet(10)
            m.pos = vec2d(uniform(self.w/2 + m.radius, self.w - m.radius), uniform(m.radius, self.h/2 - m.radius))
            m.side = 1
            self.magnets.append(m)
            
        # Load sounds
        pygame.mixer.stop()
        self.music = load_sound('music_slow.ogg')
        self.music.play(-1)
        self.playSound = True
        self.slow_music = load_sound('music_slow.ogg')
        self.end_music = load_sound('music_end.ogg')
        self.fast_music = load_sound('music_fast.ogg')
        
        # Load images
        self.char_image = load_image('ball.png', -1)
        self.pause_image = load_image('pause.png')
        
    def update(self):
        if self.pause == False:
            c = self.charactors[self.selected] # Only update the selected charactor
            
            # Tick over the charactors' timer
            c.dt = c.clock.tick()
            
            # Calculate charactor accelaration
            c.acc = self.max_acc*c.move # set accelaration along movement axis
            
            # Add in 'gravitational' accelaration
            for m in self.magnets:
                if m.side == self.selected:
                    r = m.pos - c.pos
                    r2 = r.x**2 + r.y**2
                    unit_normal = r/sqrt(r2)
                    
                    grav_acc = (self.grav_const*(m.mass/r2))*unit_normal
                    
                    c.vel += grav_acc
                    
                    if r2 <= m.radius**2:
                        c.absorbed = True
                        c.tracker = 0
                        self.create_no = 10
                        c.life += -1
                    
                    else:
                        c.absorbed = False
                        
            # Calculate charactor velocity
            c.vel += c.acc
            
            if c.vel.length > self.max_vel: # limit maximum velocity
                c.vel.length = self.max_vel
            
            new_pos = c.pos + c.vel # position after update
            # Collision with boundaries
            if new_pos.x >= self.right_limit[self.selected] or new_pos.x <= self.left_limit[self.selected]:
                c.vel.x = -c.vel.x
            if new_pos.y >= self.h or new_pos.y <= 0:
                c.vel.y = -c.vel.y
                
            # Calculate charactor posistion
            c.pos += c.vel
            c.rect.center = c.pos
            
            # Bounce magnets off the walls
            for m in self.magnets:
                new_pos = m.pos + m.vel
                if new_pos.x + m.radius >= self.right_limit[m.side] or new_pos.x - m.radius <= self.left_limit[m.side]:
                    m.vel.x = -m.vel.x
                if new_pos.y + m.radius >= self.h or new_pos.y - m.radius <= 0:
                    m.vel.y = -m.vel.y
                m.pos += m.vel
            
            # Create a bunch of particles each time step
            c.tracker += c.dt
            if c.tracker > c.create_rate:
                c.tracker = 0            
                angle = 0
                position = c.pos.inttup()
                vel = c.vel/1.5
                velocity = vel.inttup()
                if c.life < 98:
                    c.life += 3
                
                if c.absorbed == False: 
                    for p in range(self.create_no):
                        p = Particle(position)
                        angle += 360/(self.create_no)
                        p.vel.rotate(angle)
                        p.vel += vec2d(velocity)
                        self.particles.append(p)
            
            # Limit particle life
            for p in self.particles:
                p.life += -1
                p.pos += p.vel
                
                # Kill particles if they cross over the centre
                if p.pos.x < self.w/2:
                    if p.pos.x + p.vel.x >= self.w/2:
                        p.life = 0
                elif p.pos.x > self.w/2:
                    if p.pos.x + p.vel.x <= self.w/2:
                        p.life = 0
                
                # Add gravity effect for particles within a distance of a magnet.
                for m in self.magnets: 
                    if m.side == self.selected:
                        r = m.pos - p.pos
                        r2 = r.x**2 + r.y**2
                        # if r2 < self.grav_radius:
                        unit_normal = r/sqrt(r2)
                        grav_acc = (m.mass/r2)*unit_normal
                            
                        p.vel += grav_acc
                        
                        # Reduce score and stop particle production when player is absorbed
                        if r2 <= m.radius**2:
                            p.life = 0
                            m.life += -1
                            self.score += 1 + randint(0, 9)/10.0
                            if self.create_no < 20:
                                self.create_no += 1
                            if m.life == 0:
                                self.score += 10 + randint(0, 9)/10.0
                                angle = 0 + randint(0, 179)
                                for t in range(3):
                                    position = m.pos.inttup()
                                    t = Tinie(position)
                                    t.vel.angle = angle
                                    t.side = self.selected
                                    angle += 180
                                    self.tinies.append(t)
            
            # Resolve tinies velocity, if they exist
            if len(self.tinies) > 0:
                for t in self.tinies:
                    if t.pos.y + t.vel.y >= self.h:
                        t.vel.y = -t.vel.y
                    if t.pos.y + t.vel.y <= 0:
                        t.vel.y = -t.vel.y
                    if t.pos.x + t.vel.x >= self.w:
                        t.vel.x = -t.vel.x
                    if t.pos.x + t.vel.x <= 0:
                        t.vel.x = -t.vel.x
                    if t.pos.x <= self.w/2 and t.pos.x+t.vel.x > self.w/2:
                        t.vel.x = -t.vel.x
                    if t.pos.x > self.w/2 and t.pos.x+t.vel.x <= self.w/2:
                        t.vel.x = -t.vel.x
                    t.pos += t.vel
                    t.life += -1
                
                # Turn tinies into magnets
                if self.tinies[0].life < 1:
                    self.tinies = self.tinies[1:]
                    for t in self.tinies:
                        if t.life < 1:
                            m = Magnet(choice([5, 10, 15, 20]))
                            position = t.pos.inttup()
                            velocity = t.vel.inttup()
                            m.pos = vec2d(position)
                            
                            if m.pos.x > self.w/2:
                                m.side = 1
                                
                            if self.w/2 <= m.pos.x <= (self.w/2 + m.radius):
                                m.pos.x = self.w/2 + m.radius
                            elif (self.w/2 - m.radius) < m.pos.x <= self.w/2:
                                m.pos.x = self.w/2 - m.radius
                            elif m.pos.x < m.radius:
                                m.pos.x = m.radius
                            elif m.pos.x > self.w - m.radius:
                                m.pos.x = self.w - m.radius
                            elif m.pos.y < m.radius:
                                m.pos.y = m.radius
                            elif m.pos.y > self.h - m.radius:
                                m.pos.y = self.h - m.radius
                                
                            self.magnets.append(m)
            
            # Update particle and magnet list
            self.particles = [p for p in self.particles if p.life > 0]
            self.magnets = [m for m in self.magnets if m.life > 0]
            self.tinies = [t for t in self.tinies if t.life > 0]
            
            # Update score surface
            powerText = ('Power generated:')
            scoreText = (str(self.score) +' kWh')
            self.power_surf = self.score_font.render(powerText, True, (88, 88, 88))
            self.score_surf = self.score_font.render(scoreText, True, (180, 180, 180))
            
            # Update life surface
            self.pulA_surf = self.score_font.render('Pulsar A:', True, (85, 20, 63))
            self.pulB_surf = self.score_font.render('Pulsar B:', True, (0, 47, 113))
            self.scoA_surf = self.score_font.render(str(self.charactors[0].life) +'%', True, (180, 180, 180)) 
            self.scoB_surf = self.score_font.render(str(self.charactors[1].life) +'%', True, (180, 180, 180)) 
            
            if c.life < 1:
                pygame.mixer.fadeout(2000)
                pygame.time.wait(2000)
                self.running = False
                self.saveScore()
                h = Highscore().mainLoop(40)
            
            
    
    def keyDown(self, key):
        
        # Set charactor accelaration direction
        if key == K_UP: self.charactors[self.selected].move.y = -1 
        if key == K_DOWN: self.charactors[self.selected].move.y = 1
        if key == K_LEFT: self.charactors[self.selected].move.x = -1
        if key == K_RIGHT: self.charactors[self.selected].move.x = 1       
        
        # Switch sides
        if key == K_SPACE:
            self.create_no = 10
            self.particles = []
            if self.selected == 0: 
                self.selected = 1
            elif self.selected == 1: 
                self.selected = 0
        
        # Toggle sound
        if key == K_s:
            if self.playSound == True: 
                pygame.mixer.pause()
                self.playSound = False
            elif self.playSound == False:
                pygame.mixer.unpause()
                self.playSound = True
                
        if key == K_p:
            if self.pause == False:
                self.pause = True
            elif self.pause == True:
                self.pause = False
                
    def keyUp(self, key):
    
        # If player releases, and no other is selected, set acc to zero
        if key == K_UP: 
            if self.charactors[self.selected].move.y == -1:
                self.charactors[self.selected].move.y = 0
        if key == K_DOWN: 
            if self.charactors[self.selected].move.y == 1:
                self.charactors[self.selected].move.y = 0
        if key == K_LEFT: 
            if self.charactors[self.selected].move.x == -1:
                self.charactors[self.selected].move.x = 0
        if key == K_RIGHT: 
            if self.charactors[self.selected].move.x == 1:
                self.charactors[self.selected].move.x = 0
        
    def mouseUp(self, button, pos):
        pass
        
    def mouseMotion(self, buttons, pos, rel):
        pass
        
    def draw(self):
        if self.pause == True:
            self.screen.blit(self.pause_image, (0, 0))
        elif self.pause == False:
            self.screen.blit(self.background, (0, 0)) # Paste background
            # Draw charactor, baddies and particles
            for c in self.charactors:
                self.screen.blit(self.char_image, c.pos.inttup())
                
            for m in self.magnets:
                pygame.draw.circle(self.screen, (0, 0, 0), m.pos.inttup(), m.radius)
            
            for p in self.particles:
                pygame.draw.line(self.screen, (240, 8, 74), p.pos-2*p.vel, p.pos, 2)
                
            for t in self.tinies:
                pygame.draw.circle(self.screen, (240, 8, 74), t.pos.inttup(), t.radius)
            
            self.screen.blit(self.pulA_surf, (120, 20))
            self.screen.blit(self.pulB_surf, (550, 20))
            self.screen.blit(self.scoA_surf, (200, 20))
            self.screen.blit(self.scoB_surf, (630, 20))
            self.screen.blit(self.score_surf, (450, 20))
            self.screen.blit(self.power_surf, (300, 20))
            
    def saveScore(self):
        scores = open_file('archive.txt')
        name = inputbox.ask(self.screen, 'Name')
        scores.write(str(self.score) + ' ' +str(name)+ '\n')
        scores.close()


        
