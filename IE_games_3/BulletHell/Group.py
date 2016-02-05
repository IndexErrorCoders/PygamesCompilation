import pygame

class Group(object):
    def __init__(self, name, count, item):
        self.name = name
        self.num_enemies = count
        self.drop = item
        self.enemies = []
        
    def add_enemy(self, enemy):
        self.enemies.append(enemy)
        
    def remove_enemy(self, enemy):
        self.enemies.remove(enemy)
        
