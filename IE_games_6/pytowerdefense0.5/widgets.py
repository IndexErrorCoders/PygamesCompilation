# -*- coding: utf-8 -*-

import os
import sys
import random
import math

import pygame
from pygame import Rect, Color
from pygame.locals import *


class WidgetError(Exception): pass
class LayoutError(WidgetError): pass


class ImageButton(pygame.sprite.Sprite):
    def __init__(self, screen, image, rect, callback, hover_increase=12):
        """
        Takes 5 arguments:
        screen: pygame surface to blit on.
        image: image of the button. Either path to one, or a list of two paths. If a list, the second item will be shown when hovered by the mouse.
        rect: rect to blit on
        callback: Function to call when clicked
        hover_increase: Only applicable if there is only one image. Defaults to 1.20, which makes the button 20% larger when hovered by the mouse.
        """
        #Add a tooltip?
        self.screen = screen
        self.hover_increase = hover_increase
        self.imageset = []
        if image.__class__ == "".__class__:
            self.imageset = [pygame.image.load(image).convert_alpha(), self.generate_hover_pic(pygame.image.load(image).convert_alpha())] #self.generate_hover_pic(pygame.image.load(image)).convert_alpha()]
        elif image.__class__ == self.imageset.__class__ and image[0].__class__ == "".__class__ and image[1].__class__ == "".__class__:
            self.imageset = [pygame.image.load(image[0]).convert_alpha(), pygame.image.load(image[1]).convert_alpha()]
        else:
            print "ImageButton image has to be either the path to one image or a list of two paths."
        self.maxrect = Rect(rect.left, rect.top, self.imageset[1].get_size()[0], self.imageset[1].get_size()[1])
        self.rect = rect
        self.callback = callback
        self.clicked = False
        self.dirty = False
        self.lastsize = None

    def smoothscale_to_half(self, image):
        return pygame.transform.smoothscale(image, (image.get_size()[0]/ 2, image.get_size()[1] / 2))

    def generate_hover_pic(self, image):
        return pygame.transform.scale(image, (int(image.get_size()[0]+self.hover_increase), int(image.get_size()[1]+self.hover_increase)))

    def update(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(self.imageset[1], self.rect)
            if self.lastsize != "hover":
                self.dirty = True
                self.lastsize = "hover"
        else:
            self.screen.blit(self.imageset[0], self.rect)
            if self.lastsize != "normal":
                self.dirty = True
                self.lastsize = "normal"
        if self.clicked:
            self.callback()
            self.clicked = False

class TextMessage(object):
    def __init__(self, screen, text, pos, duration=1000, size=12, flashy=True, initialdelay=200, color=Color("gold")):
        self.screen = screen
        self.pos = pos
        self.size = size
        self.color = color
        self.font = pygame.font.SysFont('arial', self.size)
        self.font.set_bold(True)
        self.textstring = text
        self.text = self.font.render(text, True, color)
        self.duration = duration
        self.initialdelay = initialdelay
        self.flashy = flashy
        self.timealive = 0 #ms
        self.lastactiontime = 0 #ms
        if duration > 0:
            self.sizereductionperaction = ((size / 1.9) / duration) * 50.
            if self.sizereductionperaction >= 0.5 or self.sizereductionperaction <= 1:
                self.sizereductionperaction = 1
            else:
                self.sizereductionperaction = round(self.sizereductionperaction)

        self.xdirection = random.choice([-1, 1])
    def update(self, time_passed):
        self.timealive += time_passed
        if self.timealive - 200 > self.lastactiontime and self.flashy and self.timealive > self.initialdelay:
            self.pos[1] -= 4
            self.pos[0] += 2 * self.xdirection
            self.size -= self.sizereductionperaction
            self.font = pygame.font.SysFont('arial', self.size)
            self.font.set_bold(True)
            self.text = self.font.render(self.textstring, True, self.color)
    def draw(self):
        self.screen.blit(self.text, (self.pos[0] - (self.text.get_width() / 2) , self.pos[1] - (self.text.get_height() / 2)))

class Box(object):
    """ A rectangular box. Has a background color, and can have
        a border of a different color.

        Has a concept of the "internal rect". This is the rect
        inside the border (not including the border itself).
    """
    def __init__(self,
            surface,
            rect,
            bgcolor=(0,0,0),
            border_width=0,
            border_color=Color('black'),
            tile=None,
            alpha=False):
        """ rect:
                The (outer) rectangle defining the location and
                size of the box on the surface.
            bgcolor:
                The background color
            border_width:
                Width of the border. If 0, no border is drawn.
                If > 0, the border is drawn inside the bounding
                rect of the widget (so take this into account when
                computing internal space of the box).
            border_color:
                Color of the border.
        """
        self.surface = surface
        self.rect = rect
        if bgcolor:
            self.bgcolor = bgcolor
        else:
            self.bgcolor = None
        self.border_width = border_width
        self.border_color = border_color
        self.alpha = alpha

        # Internal rectangle
        self.in_rect = Rect(
            self.rect.left + self.border_width,
            self.rect.top + self.border_width,
            self.rect.width - self.border_width * 2,
            self.rect.height - self.border_width * 2)
        if tile:
            self.tile = pygame.image.load(tile).convert()
            self.loop = (math.ceil((self.rect.width - self.border_width * 2) / self.tile.get_size()[0]), math.ceil((self.rect.height - self.border_width * 2) / self.tile.get_size()[1]))
            mod1 = (self.rect.width - self.border_width * 2) % self.tile.get_size()[0]
            mod2 = (self.rect.height - self.border_width * 2) % self.tile.get_size()[1]
            if mod1 != 0:
                self.loop = (self.loop[0] + 1, self.loop[1])
            if mod2 != 0:
                self.loop = (self.loop[0], self.loop[1] + 1)
        else:
            self.tile = None

    def update(self, rect):
        self.rect = rect
        self.in_rect = Rect(
            self.rect.left + self.border_width,
            self.rect.top + self.border_width,
            self.rect.width - self.border_width * 2,
            self.rect.height - self.border_width * 2)
        if self.tile:
            self.loop = ((self.rect.width - self.border_width * 2) / self.tile.get_size()[0], (self.rect.height - self.border_width * 2) / self.tile.get_size()[1])

    def draw(self):
        box_border = pygame.Surface((self.rect.w, self.rect.h))
        box_border.fill(self.border_color)
        box_background = pygame.Surface((self.in_rect.w, self.in_rect.h))
        if self.bgcolor:
            box_background.fill(self.bgcolor)
        elif self.tile:
            for x in range(0, int(self.loop[0])):
                for y in range(0, int(self.loop[1])):
                    box_background.blit(self.tile, (self.tile.get_size()[0]*x,self.tile.get_size()[1]*y))
        if self.alpha:
            box_border.set_alpha(self.alpha)
            box_background.set_alpha(self.alpha)
        self.surface.blit(box_border, self.rect)
        self.surface.blit(box_background, self.in_rect)
    def get_internal_rect(self):
        """ The internal rect of the box.
        """
        return self.in_rect


class MessageBoard(object):
    """ A rectangular "board" for displaying messages on the
        screen. Uses a Box with text drawn inside.

        The text is a list of lines. It can be retrieved and
        changed with the .text attribute.
    """
    def __init__(self,
            surface,
            rect,
            text,
            font=('arial', 20),
            font_color=Color('white'),
            bgcolor=Color('gray25'),
            border_width=0,
            border_color=Color('black'),
            tooltip=False,
            game=None,
            alpha=255):
        """ rect, bgcolor, border_width, border_color have the
            same meaning as in the Box widget.

            text:
                The initial text of the message board.
            font:
                The font (a name, size tuple) of the message
            font_color:
                The font color
        """
        self.surface = surface
        if game and tooltip:
            self.rect = game.mboard.rect #Rect(660, 440, 120, 130)  #game.get_toolbox_rect()#game.get_toolbox_rect_n(game.tooltip_id) ### FIXME
        else:
            self.rect = rect
        self.text = text
        self.bgcolor = bgcolor
        self.font = pygame.font.SysFont(*font)
        self.font_color = font_color
        self.border_width = border_width

        if tooltip:
            self.active = False #default
            self.alpha = 200
        else:
            self.active = True
            self.alpha = False
        self.alpha = alpha
        self.box = Box(surface, self.rect, bgcolor, border_width, border_color, alpha=self.alpha)#, alpha=self.alpha)
    def update(self, rect):
        self.rect = rect
        self.box.update(rect)

    def draw(self):
        self.box.draw()

        # Internal drawing rectangle of the box
        #

        text_rect = Rect(
            self.rect.left + self.border_width,
            self.rect.top + self.border_width,
            self.rect.width - self.border_width * 2,
            self.rect.height - self.border_width * 2)

        x_pos = text_rect.left
        y_pos = text_rect.top

        # Render all the lines of text one below the other
        #
        for line in self.text:
            line_sf = self.font.render(line, True, self.font_color)#, self.bgcolor)

##            if (    line_sf.get_width() + x_pos > self.rect.right or
##                    line_sf.get_height() + y_pos > self.rect.bottom):
##                raise LayoutError('Cannot fit line "%s" in widget' % line)

            self.surface.blit(line_sf, (x_pos, y_pos))
            y_pos += line_sf.get_height()

class TextRectException:
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

def render_textrect(string, font, rect, text_color, background_color, justification=0): #From http://www.pygame.org/pcr/text_rect/index.php
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    import pygame

    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    # Let's try to write the text out on the surface.

    surface = pygame.Surface(rect.size)
    surface.fill(background_color)

    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException, "Invalid justification argument: " + str(justification)
        accumulated_height += font.size(line)[1]

    return surface



class TextWidget(object): #Courtesy of Mark Mruss, released under the LGPL License.
    """This is a helper class for handling text in PyGame.  It performs
    some basic highlighting and tells you when the text has been clicked.
    This is just one of the many ways to handle your text.
    This is a new-style class and I am somewhat new to them so hopefully it
    all works.
    """
    #Event
    TEXT_WIDGET_CLICK = pygame.locals.USEREVENT
    #Hand Cursor
    __hand_cursor_string = (
    "     XX         ",
    "    X..X        ",
    "    X..X        ",
    "    X..X        ",
    "    X..XXXXX    ",
    "    X..X..X.XX  ",
    " XX X..X..X.X.X ",
    "X..XX.........X ",
    "X...X.........X ",
    " X.....X.X.X..X ",
    "  X....X.X.X..X ",
    "  X....X.X.X.X  ",
    "   X...X.X.X.X  ",
    "    X.......X   ",
    "     X....X.X   ",
    "     XXXXX XX   ")
    __hcurs, __hmask = pygame.cursors.compile(__hand_cursor_string, ".", "X")
    __hand = ((16, 16), (5, 1), __hcurs, __hmask)
    #Text
    def __get_text(self):
        return self.__m_text
    def __set_text(self, text):
        if (self.__m_text != text):
            self.__m_text = text
            self.update_surface()
    def __del_text(self):
        del self.__m_text
    def __doc_text(self):
        return "The text to be displayed by the text widget"
    text = property(__get_text, __set_text, __del_text, __doc_text)
    #Colour
    def __get_colour(self):
        return self.__m_colour
    def __set_colour(self, colour):
        if (self.__m_colour != colour):
            self.__m_colour = colour
            self.update_surface()
    colour = property(__get_colour, __set_colour)
    #Size
    def __get_size(self):
        return self.__m_size
    def __set_size(self, size):
        if (self.__m_size != size):
            self.__m_size = size
            self.create_font()
    size = property(__get_size, __set_size)
    #Font Filename
    def __get_font_filename(self):
        return self.__m_font_filename
    def __set_font_filename(self, font_filename):
        if (self.__m_font_filename != font_filename):
            self.__m_font_filename = font_filename
            #Is this a full path?
            if (not os.access(self.__m_font_filename, os.F_OK)):
                #Join with the local path to try to get the full path
                self.__m_font_filename = os.path.join(self.__local_path
                    , self.__m_font_filename)
            self.create_font()
    font_filename = property(__get_font_filename, __set_font_filename)
    #Highlight
    def __get_highlight(self):
        return self.__m_highlight
    def __set_highlight(self, highlight):
        if (not(self.__m_highlight == highlight)):
            #Save the bold_rect
            if (self.__m_highlight):
                self.bold_rect = self.rect
            self.__m_highlight = highlight
            #update the cursor
            self.update_cursor()
            if (highlight):
                self.size += self.highlight_increase
            else:
                self.size -= self.highlight_increase
            if (self.highlight_increase == 0):
                self.create_font()
    highlight = property(__get_highlight, __set_highlight)
    #Show Highlight Cursor
    def __get_highlight_cursor(self):
        return self.__m_highlight_cursor
    def __set_highlight_cursor(self, highlight_cursor):
        if (self.__m_highlight_cursor != highlight_cursor):
            self.__m_highlight_cursor = highlight_cursor
            self.update_cursor()
    highlight_cursor = property(__get_highlight_cursor, __set_highlight_cursor)

    def __init__(self, text="", colour=(0,0,0), size=32
                , highlight_increase = 10, font_filename=None
                , show_highlight_cursor = True, event=TEXT_WIDGET_CLICK, bold=True):
        """Initialize the TextWidget
        @param text = "" - string - The text for the text widget
        @param colour = (0,0,0) - The colour of the text
        @param size = 32 - number - The size of the text
        @param highlight_increase - number - How large do we want the
        text to grow when it is highlighted?
        @param font_filename = None - string the patht to the font file
        to use, None to use the default pygame font.
        @param show_highlight_cursor = True - boolean - Whether or not to change
        the cursor when the text is highlighted.  The cursor will turn into
        a hand if this is true.
        """

        #inits
        self.dirty = False
        self.bold_rect = None
        self.highlight_increase = highlight_increase
        self.tracking = False
        self.rect = None
        self.event = event
        self.bold = bold

        #Get the local path
        self.__local_path = os.path.realpath(os.path.dirname(__file__))

        #property inits
        self.__m_text = None
        self.__m_colour = None
        self.__m_size = None
        self.__m_font_filename = None
        self.__m_highlight = False
        self.__m_font = None
        self.__m_highlight_cursor = False
        self.__m_rect = None

        self.text = text
        self.colour = colour
        self.size = size
        self.font_filename = font_filename
        self.highlight = False
        self.highlight_cursor = show_highlight_cursor

        self.create_font()

    def __str__(self):
        return "TextWidget: %s at %s" % (self.text, self.rect)

    def update_cursor(self):
        if (self.highlight_cursor):
            if (self.highlight):
                pygame.mouse.set_cursor(*self.__hand)
            else:
                pygame.mouse.set_cursor(*pygame.cursors.arrow)

    def create_font(self):
        """Create the internal font, using the current settings
        """
        if (self.size):
            try:
                self.__m_font = pygame.font.Font(self.font_filename
                    , self.size)
            except Exception, e:
                print("Error creating font: '%s' using file: '%s'" % (
                    str(e), self.font_filename))
                print("Trying with default font")
                self.__m_font = pygame.font.Font(None, self.size)

            self.update_surface()

    def update_surface(self):
        """Update the current surface, basically render the
        text using the current settings.
        """
        if (self.__m_font):
            if self.bold: self.__m_font.set_bold(self.highlight)
            self.image = self.__m_font.render(self.text
                , True
                , self.colour)
            self.dirty = True
            if (self.rect):
                # Used the current rects center point
                self.rect = self.image.get_rect(center=self.rect.center)
            else:
                self.rect = self.image.get_rect()

    def draw(self, screen):
        """Draw yourself text widget
        @param screen - pygame.Surface - The surface that we will draw to
        @returns - pygame.rect - If drawing has occurred this is the
        rect that we drew to.  None if no drawing has occurerd."""

        rect_return = None
        if ((self.image)  and  (self.rect) and (self.dirty)):
            if (self.bold_rect):
                """We may need to overwrite the bold text size
                This gets rid of leftover text when moving from
                bold text to non-bold text.
                """
                rect_return = pygame.Rect(self.bold_rect)
                """Set to None, since we only need to do this
                once."""
                self.bold_rect = None
            else:
                rect_return = self.rect
            #Draw the text
            screen.blit(self.image, self.rect)
            #Dirty no more
            self.dirty = False
            return rect_return

    def on_mouse_button_down(self, event):
        """Called by the main application when the
        MOUSEBUTTONDOWN event fires.
        @param event - Pygame Event object
        MOUSEBUTTONDOWN  pos, button
        """
        #Check for collision
        self.tracking = False
        if (self.rect.collidepoint(event.pos)):
            self.tracking = True

    def on_mouse_button_up(self, event):
        """Called by the main application when the
        MOUSEBUTTONDOWN event fires.
        @param event - Pygame Event object
        MOUSEBUTTONDOWN  pos, button
        """
        #Check for collision
        if ((self.tracking) and (self.rect.collidepoint(event.pos))):
            #Not Tracking anymore
            self.tracking = False
            self.on_mouse_click(event)

    def on_mouse_click(self, event):
        """Called by the main application when the
        MOUSEBUTTONDOWN event fires, and the text widget
        has been clicked on.  You can either let
        this post the event (default) or you can override this
        function call in your app.
        ie. myTextWidget.on_mouse_click = my_click_handler
        @param event - Pygame Event object
        MOUSEBUTTONDOWN  pos, button
        """
        #Create the TEXT_WIDGET_CLICK event
        event_attrib = {}
        event_attrib["button"] = event.button
        event_attrib["pos"] = event.pos
        event_attrib["text_widget"] = self
        e = pygame.event.Event(self.event, event_attrib)
        pygame.event.post(e)
