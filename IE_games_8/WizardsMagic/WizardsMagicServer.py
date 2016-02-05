# -*- coding: utf-8 -*-
#Wizards Magic Server
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
# To change this template, choose Tools | Templates
# and open the template in the editor.
#import pygame.sprite
#Внимание!! Для того, чтоsбы слои не наслаивались, я использую объект surface_backup , который является копией изображения. После этого они заменяются
#__author__ = "chubakur"
#__date__ = "$12.02.2011 12:11:42$"
#import pygame
#from pygame.locals import *
#Коды answ
#100 - NO
#200 - OK
#300 - ping packag
#400 - service message
import sys
import player
try:
    import json
except ImportError:
    import simplejson as json

import socket
import select
import threading
import cards 
import globals
import options

#host = ""
#port = 7712
sockets = [] #сокеты игроков
sockets.append([])
sockets.append([])
connections = [] #подключения
connections.append([])
connections.append([])
s = ""
num_players = 0 #tangente: remove use of num_player for inconsistence
game_id = 1 # идентификатор игры game_id=0 reserved for single player

class Connect(threading.Thread):
    def get_package(self):
        #trick to avoid blocking socket hang thread forever
        while globals.running: 
            do_read = False
            try:
                r, _, _ = select.select([self.sock], [], [], 1)
                do_read = bool(r)
            except socket.error:
                return dict(action='socket_error')
            if do_read:
                try: 
                    MSGLEN, answ = int( self.sock.recv(8) ), ''
                    while len(answ)<MSGLEN: answ += self.sock.recv(MSGLEN - len(answ))
                except ValueError: 
                    return dict(action='value_error')
                except socket.error:
                    return dict(action='socket_error')
                #print "ANSW",answ
                return json.loads(answ)
        print "Closing client connection"
        return dict(action='server_close')

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        global connections
        self.game_id = game_id
        #if players>=2:
            #   self.sock.send(json.dumps({"answ":100, "players":len(connections[self.game_id])}))
            #   return
        #self.game = False
        #self.id = num_players
        sockets[self.game_id].append(self.sock)
        connections[self.game_id].append(self)
        self.id = 0
        threading.Thread.__init__(self)
    def send(self, sock, msg):
        msg = json.dumps(msg)
        service = '%08i'%len(msg)
        #service = json.dumps(service)
        try:
            sock.send(service)
            sock.send(msg)
        except socket.error:
            pass
    def run(self):
        #global num_players,game_id
        global game_id
        while globals.running:
            query = self.get_package()
            if query['action'] == "join":
                # init deck if it is a new game
                # if num_players == 0: 
                if len(globals.players[self.game_id]) == 0: 
                    globals.games_cards[self.game_id]['water'] = cards.water_cards_deck[:]
                    globals.games_cards[self.game_id]['fire'] = cards.fire_cards_deck[:]
                    globals.games_cards[self.game_id]['air'] = cards.air_cards_deck[:] 
                    globals.games_cards[self.game_id]['earth'] = cards.earth_cards_deck[:]
                    globals.games_cards[self.game_id]['life'] = cards.life_cards_deck[:] 
                    globals.games_cards[self.game_id]['death'] = cards.death_cards_deck[:]

                #num_players+=1
                self.nickname = query['nickname']
                print "Nick: ", self.nickname
                globals.players[self.game_id].append(player.Player(self.game_id))
                self.id = len(globals.players[self.game_id]) - 1
                #globals.players[self.game_id][id].id = num_players   
                globals.players[self.game_id][self.id].id = len(globals.players[self.game_id])
                #массив игроки. Элемент 0 - 1 игрок , элемент 1 - второй игрок
                #Отправляем сообщение , что все прошло Гуд, id игрока
                self.send(self.sock, {"answ":200, "action":"join","id":globals.players[self.game_id][self.id].id})
                #if num_players == 2: #когда заходит второй игрок. раздаем карты и ману.
                if len(globals.players[self.game_id]) == 2 and game_id == self.game_id: 
                    #p_id = 0
                    #num_players = 0
                    game_id += 1
                    sockets.append([])
                    connections.append([])
                    globals.players.append([])
                    globals.games_cards.append({})                    
#                    cards.water_cards = cards.water_cards_deck[:]
#                    cards.fire_cards = cards.fire_cards_deck[:]
#                    cards.air_cards = cards.air_cards_deck[:]
#                    cards.earth_cards = cards.earth_cards_deck[:]
#                    cards.life_cards = cards.life_cards_deck[:]
#                    cards.death_cards = cards.death_cards_deck[:]
#                    for gamer in globals.players[self.game_id]: #GAMER = PLAYER. просто почему-то питон неверно обрабатывает в таком случае сообщения
#                        gamer.get_mana()
#                        gamer.get_cards()
                    deck_cards = []
                    deck_cards.append({"water": globals.players[self.game_id][0].cards['water'].keys(),"fire":globals.players[self.game_id][0].cards['fire'].keys(), "air":globals.players[self.game_id][0].cards['air'].keys(),"earth":globals.players[self.game_id][0].cards['earth'].keys(), "life":globals.players[self.game_id][0].cards['life'].keys(), "death":globals.players[self.game_id][0].cards['death'].keys()})
                    deck_cards.append({"water": globals.players[self.game_id][1].cards['water'].keys(),"fire":globals.players[self.game_id][1].cards['fire'].keys(), "air":globals.players[self.game_id][1].cards['air'].keys(),"earth":globals.players[self.game_id][1].cards['earth'].keys(), "life":globals.players[self.game_id][1].cards['life'].keys(), "death":globals.players[self.game_id][1].cards['death'].keys()})
                    for connection in connections[self.game_id]:
                        #p_id += 1
                        self.send(connection.sock,{"answ":200,"nicknames":[connections[self.game_id][0].nickname,connections[self.game_id][1].nickname] ,"action":"update","mana":[globals.players[self.game_id][0].get_mana_count(), globals.players[self.game_id][1].get_mana_count()], "deck_cards":deck_cards})
            elif query['action'] == "switch_turn":
                if self.id:
                    self.send(sockets[self.game_id][0],{"answ":200,"action":"switch_turn"})
                else:
                    self.send(sockets[self.game_id][1],{"answ":200,"action":"switch_turn"})
            elif query['action'] == "card":
                #print query
                if self.id:
                    #self.send()
                    if query['type'] == 'warrior':
                        self.send(sockets[self.game_id][0], {"answ":200,"action":"card","card":query['card'],"position":query['position'],"type":query['type']})
                    else:
                        self.send(sockets[self.game_id][0], {"answ":200,"action":"card","card":query['card'],"type":query['type']})
                else:
                    if query['type'] == 'warrior':
                        self.send(sockets[self.game_id][1], {"answ":200,"action":"card","card":query['card'],"position":query['position'],"type":query['type']})
                    else:
                        self.send(sockets[self.game_id][1], {"answ":200,"action":"card","card":query['card'],"type":query['type']})
            elif query['action'] == 'cast':
                if self.id:
                    if not query['focus']:
                        self.send(sockets[self.game_id][0], {"answ":200,"action":"cast","position":query['position'],"focus":False})
                    else:
                        self.send(sockets[self.game_id][0], {"answ":200,"action":"cast","position":query['position'],"target":query['target'],"focus":True})
                else:
                    if not query['focus']:
                        self.send(sockets[self.game_id][1], {"answ":200,"action":"cast","position":query['position'],"focus":False})
                    else:
                        self.send(sockets[self.game_id][1], {"answ":200,"action":"cast","position":query['position'],"target":query['target'],"focus":True})
            elif query['action'] == 'bye':
                try:
                    if query['player_id'] == 1:
                        self.send(sockets[self.game_id][1], {"answ":200,"action":"opponent_disconnect"})
                    else:
                        self.send(sockets[self.game_id][0], {"answ":200,"action":"opponent_disconnect"})
                except IndexError:
                    print 'Player has left, not waiting for another'
                #print "Client ",query['player_id'],"disconnected"
                self.sock.close()
                break
            elif query['action'] == 'bbye':
                self.sock.close()
                break
            elif query['action'] == 'server_close':
                try: 
                    self.send(self.sock, {"answ":200, "action":"server_close"}) #send to client signal that server is going down
                except: 
                    pass
                self.sock.close()
                break
            elif query['action'] == 'value_error':
                print 'Socket value error'
                try: 
                    self.send(self.sock, {"answ":200, "action":"bye"})
                except: 
                    pass
                self.sock.close()
                break
            elif query['action'] == 'socket_error':
                print 'Socket error. Closing.'
                try: 
                    self.sock.close()
                except: 
                    pass
                break
            else:
                print query['action']
                self.send(self.sock, {"answ":300})
        self.sock.close()

class Server(threading.Thread):
    socket = None
    def __init__(self):
        print "starting server"
        self.socket = get_socket()
        threading.Thread.__init__(self)
    def run(self):
        while globals.running:
            print "waiting for client"
            sock, addr = self.socket.accept()
            print "Client connected"
            if globals.running:
                Connect(sock, addr).start()
#        print "Closing connections"
#        global connections
#        for game in connections:
#            for conn in game:
#                try: 
#                    conn.send(conn.sock, {"answ":200, "action":"server_close"})
#                except: 
#                    pass
        print "Closing server"
        self.socket.close()

def get_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", int(globals.port)))
    s.listen(5)
    return s

def main():
    print "Starting server..."
    options.read_configuration()
    socket = get_socket()
    while True:
        print "Waiting for clients on TCP port "+globals.port
        sock, addr = socket.accept()
        Connect(sock, addr).start()

if __name__ == '__main__': main() 