"""Classes to help with physical body interaction"""

from common import pymunk
import serialize

class InvalidDimensions(Exception): """The dimensions specified for conditions were inconsistent"""
class InvalidMass(Exception): """Must be either fixed or have a mass"""


class PhysicalConditions(serialize.Serializable):
    """Represents physical parameters of an object
    
    This includes the mass, velocity, force applied, acceleration
    and the physical dimensions.
    
    """

    my_properties = (
        serialize.F('mass', 0.0, 'the mass of the object'),
        serialize.L('velocity', (0.0,0.0), 'the velocity of the object'),
        serialize.L('force', (0.0,0.0), 'the force on the object'),
        serialize.F('radius', 0.0, 'the radius of the object'),        
        serialize.F('width', 0.0, 'the width of the object'),        
        serialize.F('height', 0.0, 'the height of the object'),        
        serialize.F('friction', 0.1, 'the friction the object'),        
        serialize.F('elasticity', 1.0, 'the elasticity of the object'),      
        serialize.I('layers', 0, 'the collision layers that we are in'),  
        serialize.I('group', 0, 'the collision group that we are in'),  
        serialize.B('fixed', False, 'whether the object is fixed in place'), 
        serialize.B('update_angle', False, 'whether the rotation of the body should propagate to the actors visual'), 
        serialize.B('visual_size', False, 'whether to set the size based on the visual element of our parent actor'), 
    )
    
    def __init__(self, mass=0.0, radius=0.0, velocity=(0.0, 0.0), force=(0.0, 0.0), width=0.0, height=0.0, fixed=False,
                    friction=0.1, elasticity=1.0, group=0, layers=-1, update_angle=False, visual_size=False):
        """Initialise the conditions"""
        self.body = None
        if not mass and not fixed:
            raise InvalidMass('Mass must be specified unless the object is fixed in place')
        self.mass = mass if not fixed else pymunk.inf
        self.velocity = velocity
        self.force = force
        self.fixed = fixed
        self.friction = friction
        self.elasticity = elasticity
        self.update_angle = update_angle
        self.visual_size = visual_size
        self.group = group
        self.layers = layers
        self.space = None
        if not visual_size:
            self.setGeometry(radius, width, height)

    def init(self):
        """Initialize from serialized form"""
        super(PhysicalConditions, self).init()
        self.setGeometry(self.radius, self.width, self.height)
        self._createPhysicsObject()
                
    def setGeometry(self, radius=None, width=None, height=None):
        """Set the geometry
        
        You must specify either the radius or the width and height
        
        """
        #
        # Reality check
        if radius and (width or height):
            raise InvalidDimensions('Must specify radius or width & height, not both')
        elif not radius and not (width and height):
            raise InvalidDimensions('Must specify width & height')
        #
        if radius:
            self.geometry_type = 'circle'
        else:
            self.geometry_type = 'rectangle'
        self.radius = radius
        self.width = width
        self.height = height
        self._createPhysicsObject()
            
    def _createPhysicsObject(self):
        """Return a new physics object"""
        if self.geometry_type == 'circle':
            inertia = pymunk.moment_for_circle(self.mass, 0, self.radius, (0,0))
        else:
            inertia = pymunk.moment_for_box(self.mass, self.width, self.height)
        #
        body = pymunk.Body(self.mass, inertia)
        body.velocity = self.velocity
        body.force = self.force
        #
        if self.geometry_type == 'circle':
            shape = pymunk.Circle(body, self.radius, (0,0))
        else:
            #shape = pymunk.Poly(body, [(0, 0), (self.width, 0), 
            #                           (self.width, self.height), (0, self.height)])
            w2, h2 = self.width/2, self.height/2
            shape = pymunk.Poly(body, [(-w2,-h2), (+w2, -h2), (+w2, +h2), (-w2, +h2)])
        #
        shape.elasticity = self.elasticity
        shape.collision_type = 2
        shape.group = self.group
        shape.layers = self.layers
        shape.friction = self.friction
        self.shape = shape
        self.body = body

    def updateFrom(self, physical_conditions):
        """Update the properties and our physics object"""
        self.velocity = physical_conditions.velocity
        self.force = physical_conditions.force
        self.body.velocity = self.velocity
        self.body.force = self.force



class PhysicalBody(PhysicalConditions):
    """Physical conditions for an infinitesimal object
    
    The object has no dimensions (shape) but still
    has mass etc.
    
    """
    
    def __init__(self, mass, **kw):
        """Initialise the body"""
        #
        # We create a body with a default shape but we will remove the shape from play
        # later
        super(PhysicalBody, self).__init__(mass, radius=0.1, **kw)

    def _createPhysicsObject(self):
        """Create the object
        
        This is where we remove the shape from play so that it doesn't
        interact with anything.
        
        """
        super(PhysicalBody, self)._createPhysicsObject()
        self.shape = None
