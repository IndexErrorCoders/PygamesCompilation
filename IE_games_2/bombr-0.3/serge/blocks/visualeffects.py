"""Visual effects"""

import pygame
try:
    _arraytype = pygame.surfarray.get_arraytype()
    if _arraytype == 'numeric':
        from Numeric import UInt8 as uint8, minimum, array, Float32 as float32, Int32 as int32
    elif _arraytype == 'numpy':
        from numpy import uint8, minimum, array, float32, int32
    Numeric = True
except (ImportError, NotImplementedError):
    Numeric = None

import serge.visual
import serge.render

log = serge.common.getLogger('visual')

if not Numeric:
    ShadowLayer = lambda a, b, c, d: serge.render.Layer(a, b)
else:
    class Shadow(serge.visual.SurfaceDrawing):
        """Creates a shadow from an image"""
        
        def __init__(self, source, colour):
            """Initialise the Shadow"""
            super(Shadow, self).__init__(*source.get_size())
            self._source = source
            self._colour = colour
            self.createShadow()
            
        def createShadow(self):
            """Create the shadow now
            
            Most of the logic here from http://pygame.org/wiki/ShadowEffects
            
            """
            #
            # Create alpha of main image
            image = self._source
            ambience = float(255-self._colour[3])/255
            if image.get_masks()[3] != 0:
                image_alpha = pygame.surfarray.pixels_alpha(image)
                if ambience > 0.0:
                    shadow_alpha = (image_alpha *
                                    (1.0 - ambience)).astype(uint8)
                else:
                    shadow_alpha = image_alpha
            elif image.get_colorkey() is not None:
                image_alpha = pygame.surfarray.array_colorkey(image)
                image.unlock(); image.unlock()  # pygame 1.7 bug (fixed in 1.8).
                surface_alpha = image.get_alpha()
                if surface_alpha is not None:
                    # Do what array_colorkey should have done: use surface alpha!
                    Numeric.minimum(image_alpha, surface_alpha, image_alpha)
                if ambience > 0.0:
                    shadow_alpha = (image_alpha *
                                    (1.0 - ambience)).astype(uint)
                else:
                    shadow_alpha = image_alpha
            else:
                image_alpha = image.get_alpha()
                if image_alpha is None:
                    image_alpha = 255
                shadow_alpha = int(image_alpha * (1.0 - ambience))
            #
            # Make the shadow
            shadow = image.convert_alpha()
            shading = self.getSurface()
            shading.fill(self._colour)
            pygame.surfarray.pixels_alpha(shading)[...] = image_alpha
            shadow.blit(shading, (0, 0))
            pygame.surfarray.pixels_alpha(shadow)[...] = shadow_alpha
            #
            self.surface = shadow


    class ShadowLayer(serge.render.Layer):
        """A layer that renders with a shadow beneath it"""
        
        def __init__(self, name, order, colour, offset):
            """Initialise the ShadowLayer"""
            super(ShadowLayer, self).__init__(name, order)
            self._offset = offset
            self._colour = colour
            
        def initSurface(self, renderer):
            """Initialise the surface"""
            super(ShadowLayer, self).initSurface(renderer)
            self._shadow = Shadow(self.getSurface(), self._colour)
        
        def render(self, surface):
            """Render to a surface
            
            When rendering to the surface we first create our shadow then
            render this to the surface followed by our normal rendering.
            
            """
            self._shadow.createShadow()
            surface.blit(self._shadow.surface, self._offset)
            super(ShadowLayer, self).render(surface)


class FadingLayer(serge.render.Layer):
    """A layer that you can fade in and out"""

    def __init__(self, name, order):
        """Initialise the layer"""
        super(FadingLayer, self).__init__(name, order)
        self.visibility = 255
    
    def postRender(self):
        """After rendering the surface"""
        v = 255-self.visibility
        if v:
            self.getSurface().fill((v, v, v, v), special_flags=pygame.BLEND_RGBA_SUB)   

class FadingScreen(object):
    """Fade in and out everything"""

    def __init__(self):
        """Initialise the layer"""
        self.visibility = 255
        self.renderer = serge.engine.CurrentEngine().getRenderer()
        self.renderer.linkEvent(serge.events.E_AFTER_RENDER, self.postRender)
    
    def postRender(self, obj, arg):
        """After rendering the surface"""
        v = 255-self.visibility
        if v:
            self.renderer.getSurface().fill((v, v, v, v), special_flags=pygame.BLEND_RGBA_SUB)   

    def deleteFade(self):
        """Remove the fade"""
        self.renderer.unlinkEvent(serge.events.E_AFTER_RENDER, self.postRender)
        
        
def darkenSurf2(img, amount):
    """Darken the given surface by the given amount"""
    import numpy
    alpha = pygame.surfarray.pixels_alpha(img)
    rgbarray = pygame.surfarray.array3d(img)
    src = numpy.array(rgbarray)
    dest = numpy.zeros(rgbarray.shape)
    # Use the cross-fade technique (found in pygame documentation) to 
    # darken the image.
    dest[:] = (0, 0, 0)
    diff = (dest - src) * (amount/255.0)
    new = src + diff.astype(numpy.uint8)
    try:
        newsurf = pygame.surfarray.make_surface(new).convert_alpha()
    except Exception, err:
        # For some reason this occasionally fails - give up trying to darken
        # the image. We will end up with a bright person! Seems to be an error in pygame 1.9.1
        # http://archives.seul.org/pygame/users/Apr-2011/msg00072.html
        log.error('Convert Alpha issue on %s: %s' % (img, err))
        #
        # Try again?!
        #import pdb; a = pdb.Pdb()
        try:
            newsurf = pygame.surfarray.make_surface(new).convert_alpha()
        except Exception, err:
            return img
        log.error('Retrying seemed to succeed')
    #
    pygame.surfarray.pixels_alpha(newsurf)[:] = alpha
    return newsurf       

def darkenSurf(img, amount):
    """Darken a surface"""
    mask = pygame.surface.Surface((img.get_width(), img.get_height()))
    mask.fill((255-amount, 255-amount, 255-amount, 255-amount))
    #
    new_img = img.copy()
    new_img.blit(mask, (0,0), special_flags=pygame.BLEND_RGB_MULT)
    #
    return new_img


def fadeSurface(surface, v):
    """Fade the given suface by an amount 0 to 255 - 0 is completely faded"""
    surface.fill((v, v, v, v), special_flags=pygame.BLEND_RGBA_SUB)    
    return surface


def gaussianBlur(surface, sigma):
    """This function takes a pygame surface, converts it to a numpy array
    carries out gaussian blur, converts back then returns the pygame surface.
    """
    from scipy import signal, ndimage
    # Convert to a NumPy array.
    # In theory this should be able to be surfarray.pixels3d fro direct access.
    np_array = pygame.surfarray.array3d(surface)
    alpha = pygame.surfarray.pixels_alpha(surface)
    
    # Filter the image
    result = ndimage.filters.gaussian_filter(np_array, 
                            sigma=(sigma, sigma, 0),
                            order=0,
                            mode='reflect'
                            )
                            
    #import pdb; pdb.set_trace()
    new_alpha = ndimage.filters.gaussian_filter(alpha, sigma=(sigma, sigma), order=0, mode='reflect')

    # Convert back to a surface.  ... seems to periodically fail
    try:        
        surf = pygame.surfarray.make_surface(result).convert_alpha()
    except:
        surf = pygame.surfarray.make_surface(result).convert_alpha()
    #        
    pygame.surfarray.pixels_alpha(surf)[:] = new_alpha
    
    return surf
