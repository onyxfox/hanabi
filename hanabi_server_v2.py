#! /Library/Frameworks/Python.framework/Versions/3.7/bin/python3
import socket
import sys
import hanabi_v1
from time import sleep

addresses = ['','127.0.0.1','24.98.18.225']

IP = addresses[1]
PORT = 19272

class Server:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connections = []

    def __init__(self):
            self.s.bind((IP,PORT))
            self.s.listen(5)
            print(f'Listing on {IP}:{PORT}...')

    def run(self):
        while True:
            # Adding Connections
            conn, addr = self.s.accept()

            self.connections.append(conn)
            print(f'{addr[0]}:{addr[1]} connected.')
            sleep(15)
            conn.send(bytes('Welcome to Hanabi Online\n','utf-8'))
            break
            # Check if ready to start game
            if len(self.connections) == hanabi.numPlayers:
                # Setup
                print('Player count reached. Starting game...')
                self.players = [hanabi.Player(x+1) for x in range(hanabi.numPlayers)]
                # Play game
                self.game()
                # Win/Loss Message
                if hanabi.score > 24:
                    msg = 'Your fireworks were legendary. Everyone was speachless and will remember them forever.\n'
                elif hanabi.score > 20:
                    msg = 'Your fireworks were amazing. They will be talking about them for weeks.\n'
                elif hanabi.score > 15:
                    msg = 'Your fireworks were excellent and crowd pleasing.\n'
                elif hanabi.score > 10:
                    msg = 'Your fireworks were an honorable attempt, but quickly forgotten.\n'
                elif hanabi.score > 5:
                    msg = 'Your fireworks were mediocre. There was just a hint of scattered applause.\n'
                else:
                    msg = 'Your fireworks were horrible and booed by the crowd.\n'

                # Send End of Game Message and close sockets
                for conn in self.connections:
                    conn.send(bytes(f'\nGame Over!\nYou scored {hanabi.score} points.\n{msg}','utf-8'))
                for conn in self.connections:
                    self.connections.remove(conn)
                    conn.close()
                print('Game Finished')
                self.s.close()
                break

    def game(self):
        current = 0
        # Game Loop
        while ((hanabi.score < 25) & (any(hanabi.deck.values())) & (not all(hanabi.fuses))):#(hanabi.score < 25 & (not all(hanabi.fuses)) & any(hanabi.deck.values())):
            # Send Gameboard to all players
            for i, (player, conn) in enumerate(zip(self.players,self.connections)):
                # Send gui
                conn.send(bytes('\n\n\n\n\n','utf-8'))
                conn.send(bytes(hanabi.gui(),'utf-8'))
                conn.send(bytes(f'You are Player #{player.number}\n','utf-8'))
                # Send your hand
                conn.send(bytes(f'Your Hand:{player.show()}\n','utf-8'))
                # Create Others list
                others = (self.players[i:] + self.players[:i])[1:]
                # Send others hands to current connection
                for other in others:
                    conn.send(bytes(f'Player #{other.number}:{other.tell()}\n','utf-8'))
                if player.number != current + 1:
                    conn.send(bytes('\n\n\n\n\n','utf-8'))

            # Set current player
            currentPlayer, currentConn = (self.players[current],self.connections[current])
            # Send game question
            gameStr = '\nWhat do you want to do?\n1. Give Information (info)\n2. Discard (discard)\n3. Play (play)\n'
            currentConn.send(bytes(gameStr,'utf-8'))

            # Get response
            data = currentConn.recv(1024).decode('utf-8')


            # Main Switch Statement
            s1 = hanabi.mainSwitch(data.lower())
            if s1 == 'GIVE INFO':
                print(f'{current+1}: Information')
                # Check if any hints left
                if any(hanabi.hints):
                    # Use hint
                    hanabi.changeState(-1)
                    # Ask question
                    currentConn.send(bytes('Which player do you want to give info to?\n','utf-8'))
                    # Get player number
                    while True:
                        data = currentConn.recv(1024).decode('utf-8')
                        try:
                            d1 = int(data)
                            if d1 > hanabi.numPlayers:
                                currentConn.send(bytes('Player too large. Please choose again.\n','utf-8'))
                            elif d1 <= 0:
                                currentConn.send(bytes('Player too small. Please choose again.\n','utf-8'))
                            elif d1 == currentPlayer.number:
                                currentConn.send(bytes('Can''t select yourself. Please choose again.\n','utf-8'))
                            else:
                                currentConn.send(bytes('What info do you want to give? (Enter a color or number)\n','utf-8'))
                                break
                        except ValueError:
                            continue
                    # Which info
                    while True:
                        data = currentConn.recv(1024).decode('utf-8')
                        d2 = hanabi.infoSwitch(data.lower())
                        if d2 != None:
                            break
                        else:
                            currentConn.send(bytes('Invalid information\n','utf-8'))
                            continue
                    # Give info
                    for card, known in zip(self.players[d1-1].hand,self.players[d1-1].known):
                        if card.split()[d2] == data:
                            known[d2] = True
                else:
                    currentConn.send(bytes('No hints remaining. Chose another option','utf-8'))
                    continue
            elif s1 == 'DISCARD':
                print(f'{current +1}: Discard')
                if not all(hanabi.hints):
                    hanabi.changeState(1)
                    currentConn.send(bytes('Which card do you want to discard?\n','utf-8'))
                    # Get card to discard
                    while True:
                        d3 = currentConn.recv(1024).decode('utf-8')
                        try:
                            d3 = int(d3)
                            if d3 > len(currentPlayer.hand):
                                currentConn.send(bytes('Card too large. Choose a different number\n','utf-8'))
                                continue
                            elif d3 <= 0:
                                currentConn.send(bytes('Card too small. Choose a different number\n','utf-8'))
                                continue
                            else:
                                break
                        except ValueError:
                            currentConn.send(bytes('Which card do you want to discard?\n','utf-8'))
                            continue
                    # Add to discard
                    card = currentPlayer.hand[d3-1].split()
                    hanabi.discard[card[0]].append(int(card[1]))
                    hanabi.discard[card[0]].sort()
                    # Add new card
                    if any(hanabi.deck.values()):
                        currentPlayer.hand[d3-1] = currentPlayer.draw()
                        currentPlayer.known[d3-1] = [False, False]
                    else:
                        del currentPlayer.hand[d3-1]
                        del currentPlayer.known[d3-1]
                else:
                    currentConn.send(bytes('You can\'t discard. Choose another option','utf-8'))
                    continue
            elif s1 == 'PLAY':
                print(f'{current+1}: Play')
                # Ask question
                currentConn.send(bytes('Which card do you want to play?\n','utf-8'))

                # Choose card
                while True:
                    d4 = currentConn.recv(1024).decode('utf-8')
                    try:
                        d4 = int(d4)
                        if d4 > len(currentPlayer.hand):
                            currentConn.send(bytes('Card too large. Choose a different number\n','utf-8'))
                            continue
                        elif d4 <= 0:
                            currentConn.send(bytes('Card too small. Choose a different number\n','utf-8'))
                            continue
                        else:
                            break
                    except ValueError:
                        currentConn.send(bytes('Which card do you want to play?\n','utf-8'))
                        continue

                # Get card data
                color, num = currentPlayer.hand[d4-1].split()

                # Get highest card
                try:
                    val = hanabi.inPlay[color][-1]
                except IndexError:
                    val = 0

                # Add to gameboard
                if val + 1 == int(num):
                    # Add to play
                    hanabi.inPlay[color].append(int(num))
                    hanabi.inPlay[color].sort()
                    # Add card to score
                    hanabi.score += 1
                    # Add hint back if completing sequence
                    if int(num) == 5:
                        hanabi.changeState(1)
                else:
                    # Add to discard
                    hanabi.discard[color].append(int(num))
                    hanabi.discard[color].sort()
                    # Use fuse
                    hanabi.changeState(0)

                # Draw card
                if any(hanabi.deck.values()):
                    currentPlayer.hand[d4-1] = currentPlayer.draw()
                    currentPlayer.known[d4-1] = [False, False]
                else:
                    del currentPlayer.hand[d4-1]
                    del currentPlayer.known[d4-1]
            else:
                currentConn.send(bytes('Invalid Input','utf-8'))
                continue

            # Move to next player
            current = current + 1 if current < hanabi.numPlayers-1 else 0



# Create and run server
server = Server()
server.run()
