"""Useful blocks for visual rendering"""

import pygame

import serge.visual

class InvalidSprite(Exception): """The selected sprite was not valid"""
class InvalidParameters(Exception): """The parameters for the shape were not valid"""
class OutOfRange(Exception): """The value was outside the valid range"""
class OverlappingRanges(Exception): """The ranges for the progress bar were overlapping"""
class RangesNotContiguous(Exception): """The ranges for the progress bar had gaps in them"""

### Simple shapes ###


class Rectangle(serge.visual.SurfaceDrawing):
    """A rectangle"""
    
    def __init__(self, (w, h), colour, stroke_width=0, stroke_colour=None):
        """Initialise the rectangle"""
        super(Rectangle, self).__init__(w, h)
        self._colour = colour
        self.stroke_colour = stroke_colour 
        self.stroke_width = stroke_width
        if (stroke_width and stroke_colour) and (stroke_width > min(w, h)/2 or stroke_width < 0):
            raise InvalidParameters('Stroking width must be > 0 and less than half the smallest side (%s)' % (stroke_width,))
        self._updateSurface()
        
    def _updateSurface(self):
        """Render to a surface"""
        surface = self.clearSurface()
        if self.stroke_colour and self.stroke_width:
            #
            # If we are stroking then draw a full size rectange with the stroke colour and
            # then a smaller one with the actual fill colour
            pygame.draw.rect(surface, self.stroke_colour, (0, 0, self.width, self.height))
            pygame.draw.rect(surface, self.colour, (self.stroke_width, self.stroke_width, 
                self.width-2*self.stroke_width, self.height-2*self.stroke_width))
        else:
            pygame.draw.rect(surface, self.colour, (0, 0, self.width, self.height), self.stroke_width)

    @property
    def colour(self): return self._colour
    @colour.setter
    def colour(self, value): 
        self._colour = value
        self._updateSurface()
        
                
class Circle(serge.visual.SurfaceDrawing):
    """A circle"""
    
    def __init__(self, radius, colour, stroke_width=0, stroke_colour=None):
        """Initialise the circle"""
        super(Circle, self).__init__(radius*2, radius*2)
        self._radius = radius
        self._colour = colour
        self.stroke_colour = stroke_colour 
        self.stroke_width = stroke_width
        if (stroke_width and stroke_colour) and (stroke_width > radius or stroke_width < 0):
            raise InvalidParameters('Stroking width must be > 0 and less than the radius (%d)' % stroke_width)
        self._updateSurface()
                
    def _updateSurface(self):
        """Render to a surface"""
        self.width = self.height = self._radius*2
        surface = self.clearSurface()
        x = y = self._radius
        if self.stroke_colour and self.stroke_width:
            #
            # If we are stroking then draw a full size circle with the stroke colour and
            # then a smaller one with the actual fill colour
            pygame.draw.circle(surface, self.stroke_colour, (int(x), int(y)), self._radius)
            pygame.draw.circle(surface, self.colour, (int(x), int(y)), self._radius-self.stroke_width)
        else:
            pygame.draw.circle(surface, self.colour, (int(x), int(y)), self._radius, self.stroke_width)
           
    def setAngle(self, angle):
        """Set the angle
        
        Pass through as this is a circle!"""
        pass

    def _updateDimensions(self):
        """Update the dimensions of the drawing"""
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()
        self.cx = self.width/2
        self.cy = self.height/2

    @property
    def colour(self): return self._colour
    @colour.setter
    def colour(self, value): 
        self._colour = value
        self._updateSurface()

    @property
    def radius(self): return self._radius
    @radius.setter
    def radius(self, value): 
        self._radius = value
        self._updateSurface()
    
        
### Shapes with text ###

class RectangleText(serge.visual.Drawing):
    """A rectangle with some text on it"""
    
    def __init__(self, text, text_colour, rect_dimensions, rect_colour, font_size=12, font_name='DEFAULT', stroke_width=0, stroke_colour=None, justify='center'):
        """Initialise the drawing"""
        self.text_visual = serge.visual.Text(text, text_colour, font_name, font_size, justify)
        self.rect_visual = Rectangle(rect_dimensions, rect_colour, stroke_width, stroke_colour)
        self.width = self.rect_visual.width
        self.height = self.rect_visual.height
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        w, h = self.rect_visual.width, self.rect_visual.height
        self.rect_visual.renderTo(milliseconds, surface, (x, y))
        self.text_visual.renderTo(milliseconds, surface, (x+w/2-self.text_visual.width/2, y+h/2-self.text_visual.height/2))
        
class CircleText(serge.visual.Drawing):
    """A circle with some text on it"""
    
    def __init__(self, text, text_colour, radius, circle_colour, font_size=12, font_name='DEFAULT', stroke_width=0, stroke_colour=None, justify='center'):
        """Initialise the drawing"""
        self.text_visual = serge.visual.Text(text, text_colour, font_name, font_size, justify)
        self.circle_visual = Circle(radius, circle_colour, stroke_width, stroke_colour)
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        self.circle_visual.renderTo(milliseconds, surface, (x, y))
        self.text_visual.renderTo(milliseconds, surface, 
            (x-self.text_visual.width/2+self.circle_visual.width/2, 
             y-self.text_visual.height/2+self.circle_visual.width/2))

    def getSize(self):
        """Return the size of the drawing"""
        return [self.radius]
        
### Sprite with text ###

class SpriteText(serge.visual.Sprite):
    """A sprite with some text on it"""

    def __init__(self, text, text_colour, sprite_name, font_size=12, font_name='DEFAULT', stroke_width=0, stroke_colour=None, justify='center'):
        """Initialise the drawing"""
        super(SpriteText, self).__init__()
        self.text_visual = serge.visual.Text(text, text_colour, font_name, font_size, justify)
        sprite = serge.visual.Register.getItem(sprite_name)
        self.setImage(sprite.raw_image, (sprite.width, sprite.height), sprite.framerate, sprite.running)
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        super(SpriteText, self).renderTo(milliseconds, surface, (x, y))
        self.text_visual.renderTo(milliseconds, surface, 
                (x+self.width/2-self.text_visual.width/2, 
                 y+self.height/2-self.text_visual.height/2))

    def setText(self, text):
        """Set the text"""
        self.text_visual.setText(text)

    @property
    def text(self): return self.text_visual.text

class TextToggle(SpriteText):
    """A sprite text item that has multiple cells and can be used as a toggle
    
    You can set the cells directly of use On=0 and Off=1.
    
    """
    
    def __init__(self, *args, **kw):
        """Initialise the  TextToggle"""
        super(TextToggle, self).__init__(*args, **kw)
        #
        # Reality check - the underlying sprite must have at least two cells
        if len(self.cells) <= 1:
            raise InvalidSprite('The selected sprite does not have enough cells. Needs at least two')
        
    def setOn(self):
        """Set to on"""
        self.setCell(0)
        
    def setOff(self):
        """Set to off"""
        self.setCell(1)
        
    def toggle(self):
        """Toggle the state"""
        if self.current_cell == 0:
            self.setOff()
        else:
            self.setOn()
    
    def isOn(self):
        """Return if we are on"""
        return self.current_cell == 0
    
    def isOff(self):
        """Return if we are on"""
        return self.current_cell != 0
    
    
class Toggle(TextToggle):
    """Like a text toggle but with no text"""
    
    def __init__(self, sprite_name):
        """Initialise the toggle"""
        super(Toggle, self).__init__('', (0,0,0,0), sprite_name)



class ProgressBar(serge.visual.SurfaceDrawing):
    """A progress bar
    
    The progress bar shows a rectangle on the screen which you can
    use to show progress or represent the number of cetain items.
    The bar can be a single colour or can change colour within
    certain ranges.
        
    """

    def __init__(self, size, value_ranges, border_width=0, border_colour=(255,255,255,255)):
        """Initialise the ProgressBar"""
        super(ProgressBar, self).__init__(*size)
        self._checkRanges(value_ranges)
        self.stroke_width = 0
        self.border_width = border_width
        self.border_colour = border_colour
        self._updateSurface()
        
    def _checkRanges(self, value_ranges):
        """Check that the ranges make sense"""
        self.value_ranges = value_ranges
        last_low = last_high = None
        for low, high, colour in value_ranges:
            if last_low != None:
                if low < last_high:
                    raise OverlappingRanges('The ranges overlap (%d, %d)' % (last_high, low))
                elif low > last_high:
                    raise RangesNotContiguous('The ranges have gaps (%d, %d)' % (last_high, low))
            else:
                self._value = low
                self._colour = colour
                self._min = low
            last_low, last_high = low, high
        self._max = high
        
        
    #
    # The value property, which is used to determine the progress ammount
    @property
    def value(self): return self._value
    @value.setter
    #
    def value(self, x):
        self._value = x
        for low, high, colour in self.value_ranges:
            if low <= x < high:
                self._colour = colour
                break
        else:
            #
            # Watch out for special case of x = maximum
            if x == high:
                self._colour = colour
            else:
                raise OutOfRange('The value %s was not in the range of the progress bar' % x)
        self._updateSurface()
        
    def _updateSurface(self):
        """Update our surface"""
        self.clearSurface()
        width = float(self._value-self._min)/(self._max-self._min)*self.width
        if width != 0.0:
            pygame.draw.rect(self.getSurface(), self._colour, 
                (0, 0, width, self.height), self.stroke_width)         
        if self.border_width:   
            pygame.draw.rect(self.getSurface(), self.border_colour, (0, 0, self.width, self.height),
                 self.border_width)         

