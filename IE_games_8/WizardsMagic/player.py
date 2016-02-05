# -*- coding: utf-8 -*-
#Wizards Magic
#Copyright (C) 2011-2014  https://code.google.com/p/wizards-magic/
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import cards
import os
import random
import globals
import sockets
try: 
    import pygame
    yes_pygame = True
except ImportError:
    yes_pygame = False
import ai
current_folder = os.path.dirname(os.path.abspath(__file__))

class Player(): #Прототип игрока
    def __init__(self, game_id=0):
        self.health = 50
        self.name = "player"
        self.action_points = True #Ходил игрок, или нет
        self.game_id = game_id
        self.get_cards()
        self.mana = {}
        self.get_mana()
        self.element = "none"
        self.ai = False
        self.cards_generated = False
        self.enemy = None
    def get_self_cards(self):
        return globals.ccards_1.sprites() if self.id == 1 else globals.ccards_2.sprites()
    def get_opponent_cards(self):
        return globals.ccards_2.sprites() if self.id == 1 else globals.ccards_1.sprites()
    def damage(self, damage, enemy, cast = False):
        for card in self.get_self_cards():
            card.owner_gets_damage(damage)
        self.health -= damage
        if self.health <= 0:
            globals.gameinformationpanel.display("Game Over!")
            globals.stage = False
    def heal(self, health):
        self.health += health
    def get_mana(self):
        #маны должно быть 25 в сумме!!
        manas = ["water","fire","air","earth","life","death"]
        random.shuffle(manas) #раскидываем массив рендомно
        sum = 0
        for mana_id in xrange(0, len(manas)):
            if mana_id != len(manas) - 1:
                rand = random.randint(2,5)
                sum+=rand
                self.mana[manas[mana_id]] = rand
            else:
                self.mana[manas[mana_id]] = 25 - sum
    def get_mana_count(self): #просмотр кол-ва маны
        return [self.mana['water'], self.mana['fire'], self.mana['air'], self.mana['earth'], self.mana['life'], self.mana['death']]
    def get_cards(self, server_cards = None):
        ''' server_cards = list of cards sent from remote server '''
        self.cards = {}
        tmpcards = {}
        cards_for_sort = {}
        for element in ['water', 'fire', 'air', 'earth', 'life', 'death']: 
            tmpcards[element] = {}
            cards_for_sort[element] = []
            for i in xrange(0, 4):
                #получаем карту элемента воды
                if not server_cards: 
                    randnum = random.randint(0, len(globals.games_cards[self.game_id][element])-1)
                    card = globals.games_cards[self.game_id][element][randnum]
                    globals.games_cards[self.game_id][element].remove(card)
                else:
                    card = server_cards[element][i]
                if self.game_id == 0: 
                    tmpcards[element][card] = cards.links_to_cards[card]()
                    cards_for_sort[element].append([tmpcards[element][card].level, tmpcards[element][card]])
                else: 
                    tmpcards[element][card] = card

            if self.game_id == 0: 
                cards_for_sort[element].sort()
                for i in xrange(0,4):
                    cards_for_sort[element][i][1].position_in_deck = i
        self.cards = tmpcards.copy()

        del cards_for_sort
        del tmpcards

class Player1(Player):
    def __init__(self):
        self.id = 1
        Player.__init__(self)
class Player2(Player):
    def __init__(self):
        self.id = 2
        Player.__init__(self)
def switch_position():
    #globals.attack_started = False
    globals.attack_started.pop()
    n = globals.nickname1.name
    globals.nickname1.set_nickname(globals.nickname2.name)
    globals.nickname2.set_nickname(n)
    for cardbox in globals.cardboxes:
        cardbox.opposite = not cardbox.opposite
def me_finish_turn():
    #Добавляем ману другому игроку.
    #globals.attack_started = True
    globals.attack_started.append(True)
    globals.player.enemy.mana['water'] += 1
    globals.player.enemy.mana['fire'] += 1
    globals.player.enemy.mana['air'] += 1
    globals.player.enemy.mana['earth'] += 1
    globals.player.enemy.mana['life'] += 1
    globals.player.enemy.mana['death'] += 1
    #Меняем игрока
    try:
        pygame.mixer.music.load(current_folder+'/misc/sounds/card_attack.mp3')
    except:
        print "Unexpected error: while trying play attack sound"
    globals.playmusic()
    if globals.player.id == 1:
        globals.player = globals.player2
        globals.player.action_points = True
        for card in globals.ccards_1: #Атакуем
            kill = card.attack()
            if kill:
                card.enemy_die()
            card.used_cast = False
        for spell in globals.magic_cards: #вызываем функцию повторения магия
            spell.periodical_cast()
        for card in globals.ccards_2:
            card.turn()
            card.moves_alive += 1
        for card in globals.ccards_2:
            card.additional_turn_action()
    else:
        globals.player = globals.player1
        globals.player.action_points = True
        for card in globals.ccards_2: #Атакуем
            kill = card.attack()
            if kill:
                card.enemy_die()
            card.used_cast = False
        for spell in globals.magic_cards: #вызываем функцию повторения магия
            spell.periodical_cast()
        for card in globals.ccards_1:
            card.turn()
            card.moves_alive += 1
        for card in globals.ccards_1:
            card.additional_turn_action()
    if globals.player.ai:
        cb = ai.select_cardbox()
        if cb:
            c = ai.select_card(cb.card)
            #print 'SELECTED',c
            cb.card = c()
            cb.card.field = True
            globals.player.mana[cb.card.element] -= cb.card.level
            cb.card.parent = cb
            if globals.player.id == 1:
                globals.ccards_1.add(cb.card)
            else:
                globals.ccards_2.add(cb.card)
            cb.card.summon()
        finish_turn()
def finish_turn():
    me_finish_turn()
    sockets.query({"action":"switch_turn"})
    #switch_position()
