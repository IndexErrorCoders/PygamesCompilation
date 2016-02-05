"""Some fractal utilities"""

import random
from serge.simplevecs import Vec2d

def fractalLine(start, end, number_steps, distance_per_step, decay):
    """Return a fractal line, broken into # steps with each step being a random distance"""
    center_point = (Vec2d(start) + Vec2d(end))/2
    movement_parallel = (Vec2d(end)-Vec2d(start)).normalized()
    #
    # Decide which direction to move
    angle = 90 if random.random() > 0.5 else -90
    movement_perpendicular = movement_parallel.rotated_degrees(angle)
    #
    # Distance
    movement = movement_perpendicular * distance_per_step #*random.random()
    #
    # New point
    new_point = center_point + movement
    #
    # Now do other centers if needed
    if number_steps > 1:
        return fractalLine(start, new_point, number_steps-1, distance_per_step/decay, decay) + \
               fractalLine(new_point, end, number_steps-1, distance_per_step/decay, decay)[1:]
    else:
        return [start, new_point, end]
        
        
def fractalShape(points, number_steps, distance_per_step, decay):
    """Return a shape where the straight lines are converted to fractal lines"""
    #
    # Ready to stop?
    if len(points) <= 1:
        return points
    #
    # Convert the shape
    return fractalLine(points[0], points[1], number_steps, distance_per_step, decay)[:-1] + \
           fractalShape(points[1:], number_steps, distance_per_step, decay)
    
