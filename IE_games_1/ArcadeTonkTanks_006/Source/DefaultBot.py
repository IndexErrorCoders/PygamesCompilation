# DefaultBot: driving around randomly and shooting without aiming.
# When a wall is hit, DefaultBot turn to a random direction while trying to spray bullets.
# DefaultBot tries to turn towards the middle of the arena when hitting the outer borders.

import random
from Source import GameData

def DefaultBot(tank):
    """A very simple AI"""
    action=random.random()*100
    if action < 20:
        tank.command_queue.append("up")
        tank.command_queue.append("up")
    if action > 20 and action < 30:
        tank.command_queue.append("left")
    if action > 30 and action < 40:
        tank.command_queue.append("right")
    if action == 40:
        for t in range(0,6):
            tank.command_queue.append("left")
            tank.command_queue.append("shoot")
    if action == 50:
        for t in range(0,6):
            tank.command_queue.append("right")
            tank.command_queue.append("shoot")
    if action == 45:
        tank.command_queue.append("left")
        tank.command_queue.append("shoot")
        tank.command_queue.append("right")
        tank.command_queue.append("right")
        tank.command_queue.append("shoot")
        tank.command_queue.append("left")
        tank.command_queue.append("shoot")
    # increase triggerhappiness to make the game more difficult
    if action > 100 - GameData.triggerhappiness:
        tank.command_queue.append("shoot")
    # Avoid walls in a random direction
    for wall in GameData.battleground[GameData.battlegroundnr].walls:
        if wall.colliderect(tank.rect):
            if random.random() < 0.5:
                for i in range(0,int(random.random() * 450 / GameData.angle)):
                    tank.command_queue.append("left")
                    tank.command_queue.append("shoot")
                tank.command_queue.append("flush")
            else:
                for i in range(0,int(random.random() * 450 / GameData.angle)):
                    tank.command_queue.append("right")
                    tank.command_queue.append("shoot")
                tank.command_queue.append("flush")
    # Avoid water in a random direction
    for pool in GameData.battleground[GameData.battlegroundnr].water:
        if pool.colliderect(tank.rect):
            if random.random() < 0.5:
                for i in range(0,int(random.random() * 450 / GameData.angle)):
                    tank.command_queue.append("shoot")
                    tank.command_queue.append("left")                    
                tank.command_queue.append("flush")
            else:
                for i in range(0,int(random.random() * 450 / GameData.angle)):
                    tank.command_queue.append("shoot")
                    tank.command_queue.append("right")
                tank.command_queue.append("flush")
    # Avoid borders and turn towards the centre of the arena
    if (tank.y < 60) and (tank.angle < 180):
        if tank.x < 400:
            for i in range(0,int(120/GameData.angle)):
                tank.command_queue.append("right")
            tank.command_queue.append("shoot")
            for i in range(0,int(10)):
                tank.command_queue.append("pass")
            tank.command_queue.append("flush")
        else:
            for i in range(0,int(120/GameData.angle)):
                tank.command_queue.append("left")
            tank.command_queue.append("shoot")
            for i in range(0,int(10)):
                tank.command_queue.append("pass")
            tank.command_queue.append("flush")
    elif tank.y > 668 and (tank.angle > 180):
        if tank.x < 400:
            for i in range(0,int(120/GameData.angle)):
                tank.command_queue.append("left")
            tank.command_queue.append("shoot")
            for i in range(0,int(10)):
                tank.command_queue.append("pass")
            tank.command_queue.append("flush")
        else:
            for i in range(0,int(120/GameData.angle)):
                tank.command_queue.append("right")
            tank.command_queue.append("shoot")
            for i in range(0,int(10)):
                tank.command_queue.append("pass")
            tank.command_queue.append("flush")
    elif tank.x > 705 and ((tank.angle < 90) or (tank.angle > 270)):
        if tank.y < 400:
            for i in range(0,int(120/GameData.angle)):
                tank.command_queue.append("right")
            tank.command_queue.append("shoot")
            for i in range(0,int(10)):
                tank.command_queue.append("pass")
            tank.command_queue.append("flush")
        else:
            for i in range(0,int(120/GameData.angle)):
                tank.command_queue.append("left")
            tank.command_queue.append("shoot")
            for i in range(0,int(10)):
                tank.command_queue.append("pass")
            tank.command_queue.append("flush")
    elif tank.x < 60 and (90 < tank.angle < 270):
        if tank.y < 400:
            for i in range(0,int(120/GameData.angle)):
                tank.command_queue.append("left")
            tank.command_queue.append("shoot")
            for i in range(0,int(10)):
                tank.command_queue.append("pass")
            tank.command_queue.append("flush")
        else:
            for i in range(0,int(120/GameData.angle)):
                tank.command_queue.append("right")
            tank.command_queue.append("shoot")
            for i in range(0,int(10)):
                tank.command_queue.append("pass")
            tank.command_queue.append("flush")
