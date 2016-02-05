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
import socket
import globals
try:
    import json
    print 'JSON'
except ImportError:
    import simplejson as json
    print 'SIMPLEJSON'
#host = "drakmail.ru"
#port = 7712
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def connect():
    global sock
    host = globals.server
    port = globals.port
    print host,port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, int(port)))
    except:
        return 0
    return 1
def get_package():
    #print "SERVICE:"
    #print service_package
    try: 
        MSGLEN, answ = int( sock.recv(8) ), ''
    except ValueError: #empty string (socked closed?)
        return dict(action='value_error')
    except socket.error:
        return dict(action='socket_error')

    while len(answ)<MSGLEN: answ += sock.recv(MSGLEN - len(answ))
        #return answ
    print "GET_PACKAGE RETURN"
    print answ
    return json.loads(answ)

def query_(query):
    query = json.dumps(query)
    service = '%08i'%len(query)
    sock.send(service)
    sock.send(query)
query = lambda x: x
    #print sock.recv(1)
    #return
    #return get_package()62.176.21.105

