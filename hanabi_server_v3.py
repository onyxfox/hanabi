#! /Library/Frameworks/Python.framework/Versions/3.7/bin/python3
import socket, select, sys
from random import choice, randint
from pickle import dumps, loads

addresses = ['','127.0.0.1','24.98.18.225']

IP = addresses[0]
PORT = 19272

# Set Player Number
if len(sys.argv) == 1:
    total = randint(2,5)
else:
    total = int(sys.argv[1])
print(f'{total} People Playing')

class Server:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connections = []

    def __init__(self):
        self.s.bind((IP,PORT))
        self.s.listen(5)
        print(f'Listing on {IP}:{PORT}...')

    def setup(self):
        while len(self.connections) < total:
            # Adding Connections
            conn, addr = self.s.accept()
            data = pack(len(self.connections))
            conn.send(dumps(data))
            self.connections.append(conn)
            print(f'{addr[0]}:{addr[1]} connected.')

    def run(self):
        while True:
            if len(self.connections) == total:
                pass
            else:
                print('SERVER: Lost a player shutting down')
                break
            r_sockets, w_sockets, e_sockets = select.select(self.connections,[],[])
            for socket in r_sockets:
                try:
                    data = socket.recv(1024)
                    print(data.__sizeof__())
                    if data:
                        self.broadcast(data)
                        continue
                    else:
                        socket.close()
                        self.connections.remove(socket)
                        continue
                except:
                    socket.close()
                    self.connections.remove(socket)
                    continue
        for conn in self.connections:
            conn.close()
        self.s.close()
        sys.exit()

    def broadcast(self,data):
        for conn in self.connections:
            try:
                conn.sendall(data)
            except:
                conn.close()
                self.connections.remove(conn)


def draw_card(deck):
    color = choice(list(deck.keys()))
    while len(deck.get(color)) == 0:
        color = choice(list(deck.keys()))
    index = randint(0,len(deck.get(color))-1)
    card = f'{color} {deck.get(color)[index]}'
    del deck.get(color)[index]
    return card

def pack(player_num):
    data = {
        'player info' : (0, total, 0), # current player, total players, counter
        'player num' : player_num,
        'fuses' : [True, True, True, True],
        'hints' : [True, True, True, True, True, True, True, True],
        'deck' : deck,
        'discard' : {
            'magenta': [],
            'yellow':  [],
            'green':   [],
            'blue':    [],
            'red':     [],
            },
        'played' : {
            'magenta': [],
            'yellow':  [],
            'green':   [],
            'blue':    [],
            'red':     [],
        },
        'known' : known,
        'hands' : hands
        }
    return data

deck = {
    'magenta': [1,1,1,2,2,3,3,4,4,5],
    'yellow': [1,1,1,2,2,3,3,4,4,5],
    'green': [1,1,1,2,2,3,3,4,4,5],
    'blue': [1,1,1,2,2,3,3,4,4,5],
    'red': [1,1,1,2,2,3,3,4,4,5],
    }
hands = [ [draw_card(deck) for _ in range(5-total//4)] for _ in range(total) ]
known = [ [[0,0] for _ in range(5-total//4)] for _ in range(total) ]

# Create and run server
if __name__=='__main__':
    server = Server()
    server.setup()
    server.run()
else:
    d1 = dumps(pack(0))
    print(d1.__sizeof__())
