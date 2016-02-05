import sys
import pygame

from utils import Timer


class SimpleAnimation(object):
    """ A simple animation. Scrolls cyclically through a list of
        images, drawing them onto the screen in the same posision.
    """
    def __init__(self, screen, pos, images, scroll_period, duration=-1):
        """ Create an animation.

            screen: The screen to which the animation will be drawn
            pos: Position on the screen
            images:
                A list of surface objects to cyclically scroll through
            scroll_period:
                Scrolling period (in ms)
            duration:
                Duration of the animation (in ms). If -1, the
                animation will have indefinite duration.
        """
        self.screen = screen
        self.images = images
        self.pos = pos
        self.img_ptr = 0
        self.active = True
        self.duration = duration

        self.scroll_timer = Timer(scroll_period, self._advance_img)
        self.active_timer = Timer(duration, self._inactivate, True)

    def is_active(self):
        """ Is the animation active ?

            An animation is active from the moment of its creation
            and until the duration has passed.
        """
        return self.active

    def update(self, time_passed):
        """ Update the animation's state.

            time_passed:
                The time passed (in ms) since the previous update.
        """
        for timer in [self.scroll_timer, self.active_timer]:
            timer.update(time_passed)

    def draw(self):
        """ Draw the animation onto the screen.
        """
        if self.active:
            cur_img = self.images[self.img_ptr]
            self.draw_rect = cur_img.get_rect().move(self.pos)
            self.screen.blit(cur_img, self.draw_rect)

    def _inactivate(self):
        if self.duration >= 0:
            self.active = False

    def _advance_img(self):
        self.img_ptr = (self.img_ptr + 1) % len(self.images)

class OverlayAnimation(SimpleAnimation):
    """Subclass of SimpleAnimation adapted for effects placed as an overlay on enemies"""
    def __init__(self, screen, object, origpos, images, scroll_period, duration=-1):
        SimpleAnimation.__init__(self, screen, origpos, images, scroll_period, duration)
        self.object = object
    def update(self, time_passed):
        """ Update the animation's state.
             time_passed:
                The time passed (in ms) since the previous update.
        """
        for timer in [self.scroll_timer, self.active_timer]:
            timer.update(time_passed)
        # Make sure the bottom of the effect is facing the same way as the target.
        # Since our direction vector is in screen coordinates
        # (i.e. right bottom is 1, 1), and rotate() rotates
        # counter-clockwise, the angle must be inverted to
        # work correctly.
        #
        cur_img = self.images[self.img_ptr]
        self.cur_img = pygame.transform.rotate(
            cur_img, -self.object.direction.angle)
        # When the image is rotated, its size is changed.
        self.image_w, self.image_h = self.cur_img.get_size()

    def draw(self):
        """ Draw the animation onto the screen.
        """
        if self.active:
            #cur_img = self.images[self.img_ptr] #defined in update instead
            #self.draw_rect = self.cur_img.get_rect().move(self.pos)
            #self.screen.blit(self.cur_img, self.draw_rect)
            self.draw_rect = self.cur_img.get_rect().move(
                self.object.pos.x - self.image_w / 2,
                self.object.pos.y - self.image_h / 2)
            self.object.screen.blit(self.cur_img, self.draw_rect)



if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((300, 300), 0, 32)

    clock = pygame.time.Clock()
    explosion_img = pygame.image.load('images/explosion1.png').convert_alpha()
    images = [explosion_img, pygame.transform.rotate(explosion_img, 90)]

    expl = SimpleAnimation(screen, (100, 100), images, 100, 2120)

    while True:
        time_passed = clock.tick(50)

        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        expl.update(time_passed)
        expl.draw()

        pygame.display.flip()

