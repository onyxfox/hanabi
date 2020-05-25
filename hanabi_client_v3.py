#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3
import socket, threading, sys
import firework
from tkinter import *
from pickle import dumps, loads
from random import choice, randint

IP = '127.0.0.1'#'24.98.18.225'
PORT = 19272

# initialize root window
root = Tk()
root.title("Hanabi")
root.geometry('890x550')
root.configure(bg='#1F1F1F')
root.resizable(False, False)

# Setup
main_text = StringVar()
old_text = ''
fuse_colors = ['#E9D700', '#D95700', '#CB0000', '#750E0E']
current_player, total_players, counter = ('','','')
deck, fuses, hints = [],[],[]
played, discard = [],[]
hands, known  = [], []
my_hand, my_known = [],[]

# Create title
title_bar = Label(root, textvariable=main_text, pady=8, fg='#FFFFFF', bg='#474747', font=('Arial', 24, "bold"))
title_bar.grid(column=0,row=0,columnspan=3, sticky=E+W)
main_text.set('If you see this message an error has occured.')


class Card:
    def __init__(self, canvas, pos, val=['',''], type='play', show=[True, True]):
        self.canvas = canvas
        self.color = val[0] if val[0] != 'yellow' else '#E9D700'
        self.color = self.color if show[0] else 'black'
        self.num = val[1] if show[1] else '#'
        if val == ['0','0']:
            self.options = {'fill':'white', 'outline':'black', 'tags':'zero', 'smooth':True}
            self.id = canvas.create_polygon(self.round_rectangle(pos[0],pos[1],pos[0]+55,pos[1]+89, radius=13), self.options)
        elif type == 'play':
            self.options = {'fill':'white', 'outline':'black', 'tags':'played', 'smooth':True}
            self.id = canvas.create_polygon(self.round_rectangle(pos[0],pos[1],pos[0]+55,pos[1]+89, radius=13), self.options)
            canvas.create_text(pos[0]+5,pos[1], text=self.num, anchor=N+W, fill=self.color, font=('Arial', 16))
            canvas.create_text(pos[0]+50,pos[1]+89, text=self.num, anchor=S+E, fill=self.color,  font=('Arial', 16))
            canvas.create_oval(pos[0]+22,pos[1]+39,pos[0]+22+13,pos[1]+39+13, fill=self.color, width=0)
        elif type == 'info':
            if show[0]:
                self.options = {'fill':self.color, 'outline':'black', 'tags':type, 'smooth':True}
                self.id=canvas.create_polygon(self.round_rectangle(pos[0],pos[1],pos[0]+55,pos[1]+89, radius=13),self.options)
            else:
                self.options = {'fill':'white', 'outline':'black', 'tags':type, 'smooth':True}
                self.id=canvas.create_polygon(self.round_rectangle(pos[0],pos[1],pos[0]+55,pos[1]+89, radius=13),self.options)
                canvas.create_text(pos[0]+27,pos[1]+44, text=self.num, fill='black', font=('Arial', 40))
        else:
            self.options = {'fill':'black', 'outline':'white', 'tags':type,'smooth':True}
            self.id = canvas.create_polygon(self.round_rectangle(pos[0],pos[1],pos[0]+89,pos[1]+55, radius=13), self.options)

    def round_rectangle(self, x1, y1, x2, y2, radius):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return points


# Draw Player Hands
def draw_hands():
    global hands, total_players
    locations = [[], [4,5,6,7,8,9,10,11], [8], [7,9], [6,8,10], [5,7,9,11]]
    others = hands[player_num:] + hands[:player_num]
    if total_players >= 4:
        [Card(tiles[4], pos=[k*30 + 76, 0], val=card.split(), show=my_known[k]) for k, card in enumerate(my_hand)]
        for location, hand in zip(locations[total_players], others[1:]):
            [Card(tiles[location], pos=[k*30 + 76, 0], val=card.split()) for k, card in enumerate(hand)]
    elif total_players >= 2:
        [Card(tiles[4], pos=[k*22 + 76, 0], val=card.split(), show=my_known[k]) for k, card in enumerate(my_hand)]
        for location, hand in zip(locations[total_players], others[1:]):
            [Card(tiles[location], pos=[k*22 + 76, 0], val=card.split()) for k, card in enumerate(hand)]
    else:
        for location in locations[total_players]:
            [Card(tiles[location], pos=[k*22 + 76, 0]) for k in range(5)]
def kill_hands():
    for tile in tiles[4:]:
        tile.delete(ALL)

# Draw Hints & Fuses
def draw_status():
    # Create Hints and Fuses
    for i, hint_val in enumerate(hints):
        if hint_val:
            options = {'fill':'#0000F0', 'outline':'#1F1F1F', 'tags':f'hint{2*x+0}'}
            tiles[2].create_oval(i*34+12, 10+(i%2)*34, i*34+46, 44+(i%2)*34, options)
        else:
            options = {'fill':'#1F1F1F', 'outline':'#0000F0', 'tags':f'hint{2*x+0}'}
            tiles[2].create_oval(i*34+12, 10+(i%2)*34, i*34+46, 44+(i%2)*34, options)
    for j, fuse_val, in enumerate(fuses):
        if fuse_val:
            tiles[3].create_oval(j*66+32, 28, j*66+66, 62, fill=fuse_colors[j], outline='#1F1F1F', tags=f'fuse{j}')
        else:
            tiles[3].create_oval(j*66+32, 28, j*66+66, 62, fill='#1F1F1F', outline=fuse_colors[j], tags=f'fuse{j}')
def kill_status():
    tiles[2].delete(ALL)
    tiles[3].delete(ALL)

# Drawing functions
def draw_info():
    # Color Tiles
    Card(canvas=tiles[0], pos=[10,1], val=['magenta',0], type='info', show=[True, False])
    Card(canvas=tiles[0], pos=[65,1], val=['yellow',0], type='info', show=[True, False])
    Card(canvas=tiles[0], pos=[120,1], val=['green',0], type='info', show=[True, False])
    Card(canvas=tiles[0], pos=[175,1], val=['blue',0], type='info', show=[True, False])
    Card(canvas=tiles[0], pos=[230,1], val=['red',0], type='info', show=[True, False])
    # Number Tiles
    Card(canvas=tiles[0], pos=[10,91], val=['',1], type='info', show=[False, True])
    Card(canvas=tiles[0], pos=[65,91], val=['',2], type='info', show=[False, True])
    Card(canvas=tiles[0], pos=[120,91], val=['',3], type='info', show=[False, True])
    Card(canvas=tiles[0], pos=[175,91], val=['',4], type='info', show=[False, True])
    Card(canvas=tiles[0], pos=[230,91], val=['',5], type='info', show=[False, True])
def draw_discard():
    global discard
    for j, k in enumerate(discard):
        for i, num in enumerate(discard[k]):
            val1 = 22*i + 10
            val2 = 20*j + 10
            card = Card(canvas=tiles[0], pos=[val1,val2], val=[k, num])
def draw_played():
    global played
    for i, k in enumerate(played):
        for j, num in enumerate(played[k]):
            val1 = 55*i + 10
            val2 = 20*j + 10
            card = Card(canvas=tiles[0], pos=[val1,val2], val=[k, num])
def kill_played():
    tiles[0].delete(ALL)

# Event functions
def show_deck(event):
    global old_text, deck
    old_text = main_text.get()
    # deck = data['deck']
    msg = f'Cards Left In Deck: {sum([len(v) for v in deck.values()])}'
    main_text.set(msg)

def hide_deck(event):
    global old_text
    if main_text.get()[:19] == 'Cards Left In Deck:':
        main_text.set(old_text)

def show_discard(event):
    global old_text
    old_text = main_text.get()
    main_text.set('Showing Discard')
    kill_played()
    draw_discard()

def hide_discard(event):
    global old_text
    if main_text.get() == 'Showing Discard':
        main_text.set(old_text)
    kill_played()
    if old_text == 'What info do you want to give?':
        draw_info()
    else:
        draw_played()

def show_help(event):
    global old_text
    old_text = main_text.get()
    main_text.set('Click to learn more!')

def hanabi_help(event):
    help = Toplevel()
    help.title("Help")
    help.configure(bg='#1F1F1F')
    help_msg = (
'''Hanabi Rules

This is a game of multiplayer blind cooperative solitare.
Your goal is to work together to create the best firework
display that you can by placing down cards of various
color in accending order. Sounds easy right? There is one
small catch. You can't see your own hand!! On your turn
you can do one of three options. You can:

1. Give Information - Choose another player to give either
    color or number information about their cards. All
    cards with the given inforamtion is shown. Giving
    a hint removes a hint token. If there are none left
    you can't give any more info.

2. Discard - Choose a card from your hand to place in the
    discard pile. You get a hint back, but be careful
    since the card is lost forever. There is only a few
    of each card. There are 3 ONES, 2 TWOS, 2 THREES,
    2 FOURS, and 1 FIVE of each color.

3. Play - Choose a card to try add to the fireworks show.
    If the card is placeable, congrats you are one step
    closer to finishing. Completing a firework set gives
    a hint back. If it can not be placed then it
    goes into the discard pile and you blow a fuse.

Ending the Game:
The game ends if all fireworks are successfully placed,
all four fuses are blown, or the deck runs out of cards.
If no cards remain each player gets one final turn. Your
score is the sum of the highest number of each color.
''')
    Label(help, text=help_msg, fg='white', bg='#1F1F1F', font=('Arial',18)).pack()

def hide_help(event):
    global old_text
    if main_text.get() == 'Click to learn more!':
        main_text.set(old_text)

# Create Deck and Discard and Help Icons
def accessories():
    deck_icon = Card(canvas=tiles[1], pos=[15,17], type='deck')
    discard_icon = Card(canvas=tiles[1], pos=[192,17], type='discard')
    tiles[1].create_text(60,44, text='Deck', fill='white', tags='deck')
    tiles[1].create_text(236,44, text='Discard', fill='white', tags='discard')
    tiles[1].create_oval(121,18,176,73, fill='#848482', width=0, tags='help')
    tiles[1].create_text(148, 45, text='?', font=('Arial', 36, 'bold'), tags='help')
    tiles[1].tag_bind('deck', '<Enter>', show_deck)
    tiles[1].tag_bind('deck', '<Leave>', hide_deck)
    tiles[1].tag_bind('discard', '<Enter>', show_discard)
    tiles[1].tag_bind('discard', '<Leave>', hide_discard)
    tiles[1].tag_bind('help', '<Enter>', show_help)
    tiles[1].tag_bind('help', '<Button-1>', hanabi_help)
    tiles[1].tag_bind('help', '<Leave>', hide_help)

# General Functions
def data_thread(conn, player_num):
    global info_btn, disc_btn, play_btn
    while True:
        d1 = conn.recv(1024)
        if d1:
            data = loads(d1)
            unpack(data)
            global current_player, counter, fuses, deck, played
            score = sum([len(v) for v in played.values()])
            if not any(fuses) or score >= 25 or (not any(deck.values()) and counter == total_players+1):
                end_game(score)
                break
            if current_player == player_num:
                main_text.set('What would you like to do?')
                info_btn.config(state=NORMAL)
                disc_btn.config(state=NORMAL)
                play_btn.config(state=NORMAL)
        else:
            break
        kill_played()
        kill_status()
        kill_hands()
        draw_played()
        draw_status()
        draw_hands()
    conn.close()
    sys.exit()

def unpack(data):
    global current_player, total_players, player_num, counter, fuses, hints
    global deck, played, discard, hands, known, my_hand, my_known
    current_player, total_players, counter = data['player info']
    fuses   = data['fuses']
    hints   = data['hints']
    deck    = data['deck']
    played  = data['played']
    discard = data['discard']
    hands   = data['hands']
    known   = data['known']
    my_hand = data['hands'][player_num]
    my_known= data['known'][player_num]

def pack():
    global current_player, total_players, counter, fuses, hints
    global deck, discard, played, known, hands
    current_player = (current_player+1)%total_players
    counter = counter + 1 if not any(deck.values()) else counter
    data = {
        'player info' : (current_player, total_players, counter),
        'fuses' : fuses,
        'hints' : hints,
        'deck' : deck,
        'discard' : discard,
        'played' : played,
        'known' : known,
        'hands' : hands
        }
    return data

def send_data():
    global conn
    data = pack()
    d1 = dumps(data)
    conn.send(d1)

def draw_card():
    global deck
    if not any(deck.values()):
        return '0 0'
    color = choice(list(deck.keys()))
    while len(deck.get(color)) == 0:
        color = choice(list(deck.keys()))
    index = randint(0,len(deck.get(color))-1)
    card = f'{color} {deck.get(color)[index]}'
    del deck.get(color)[index]
    return card

def post_info(event,info_idx):
    global hands, known
    x = (event.x-10)//55
    y = 0 if event.y <= 90 else 1
    converter = {
        '00':'magenta',
        '10':'yellow' ,
        '20':'green'  ,
        '30':'blue'   ,
        '40':'red'    ,
        '01':'1'      ,
        '11':'2'      ,
        '21':'3'      ,
        '31':'4'      ,
        '41':'5'      ,
    }
    info = converter.get(f'{x}{y}')
    for card, other_known in zip(hands[info_idx], known[info_idx]):
        if card.split()[y] == info:
            other_known[y] = 1
    kill_played()
    draw_played()
    main_text.set('Waiting for your turn...')
    send_data()

def peri_info(event):
    main_text.set('What info do you want to give?')
    converter = {5:6, 6:5, 7:6, 8:7, 9:8, 0:9, 1:10, 2:11}
    val = converter.get(int(str(event.widget)[-1]))
    if val == 5 or val == 6:
        info_idx = (player_num+1)%total_players
    elif val == 7:
        info_idx = (player_num+1)%total_players if total_players == 3 else (player_num+2)%total_players
    elif val == 8:
        info_idx = (player_num+2)%total_players if total_players == 4 else (player_num+1)%total_players
    elif val == 9:
        info_idx = (player_num+3)%total_players if total_players == 5 else (player_num+2)%total_players
    elif val == 10:
        info_idx = (player_num+3)%total_players
    elif val == 11:
        info_idx = (player_num+4)%total_players
    kill_played()
    draw_info()
    tiles[0].bind('<Button-1>', lambda e, *i: post_info(e,info_idx))
    locations = [[], [4,5,6,7,8,9,10,11], [8], [7,9], [6,8,10], [5,7,9,11]]
    for loc in locations[total_players]:
        tiles[loc].bind('<Button-1>', lambda e: None)

def pre_info():
    try:
        idx = hints.index(True)
        tiles[2].itemconfig(f'hint{idx}', fill='#1F1F1F', outline='#0000FF')
        hints[idx] = False
        main_text.set('Choose player to give info to.')
        kill_status()
        draw_status()
        info_btn.config(state=DISABLED)
        disc_btn.config(state=DISABLED)
        play_btn.config(state=DISABLED)
        locations = [[], [4,5,6,7,8,9,10,11], [8], [7,9], [6,8,10], [5,7,9,11]]
        for loc in locations[total_players]:
            tiles[loc].bind('<Button-1>', peri_info)
    except ValueError:
        main_text.set('You can\'t give a hint. Try a different action.')

def post_discard(event):
    global my_hand, discard, my_known
    val = 30 if total_players >= 4 else 22
    for i in range(5-total_players//4):
        if (val*i+76 <= event.x and event.x < val*i+76+val or
            (event.x>val*(4-total_players//4)+76) and i==4-total_players//4):
            color, num = my_hand[i].split()
            discard[color].append(num)
            my_hand[i]  = draw_card()
            my_known[i] = [0,0]
            kill_hands()
            draw_hands()
            for id in tiles[4].find_all():
                tiles[4].tag_unbind(id, '<Button-1>')
            main_text.set('Waiting for your turn...')
            send_data()

def pre_discard():
    global my_hand, hints
    try:
        idx = hints.index(False)
        tiles[2].itemconfig(f'hint{idx}', fill='#0000FF', outline='#1F1F1F')
        hints[idx] = True
        main_text.set('Choose which card you want to discard.')
        info_btn.config(state=DISABLED)
        disc_btn.config(state=DISABLED)
        play_btn.config(state=DISABLED)
        for id in tiles[4].find_all():
            tiles[4].tag_bind(id, '<Button-1>', post_discard)
    except ValueError:
        main_text.set('You can\'t discard a card. Try a different action.')

def post_play(event):
    global hints, fuses, my_hand, my_known, discard, played
    val = 30 if total_players >= 4 else 22
    for i in range(5-total_players//4):
        if (val*i+76 <= event.x and event.x < val*i+76+val or
            (event.x>val*(4-total_players//4)+76) and i==4-total_players//4):

            color, num = my_hand[i].split()
            val1 = played[color][-1] if played[color] else 0
            if int(num) == val1 + 1:
                played[color].append(int(num))
                if int(num) == 5:
                    try:
                        idx = hints.index(False)
                        tiles[2].itemconfig(f'hint{idx}', fill='#0000FF', outline='#1F1F1F')
                        hints[idx] = True
                    except ValueError:
                        pass
            else:
                idx = fuses.index(True)
                tiles[3].itemconfig(f'fuse{idx}', fill='#1F1F1F', outline=fuse_colors[idx])
                fuses[idx] = False
                discard[color].append(int(num))
            my_hand[i]  = draw_card()
            my_known[i] = [0,0]
            kill_hands()
            kill_played()
            draw_hands()
            draw_played()
            for id in tiles[4].find_all():
                tiles[4].tag_unbind(id, '<Button-1>')
            main_text.set('Waiting for your turn...')
            send_data()

def pre_play():
    main_text.set('Choose which card you want to play.')
    info_btn.config(state=DISABLED)
    disc_btn.config(state=DISABLED)
    play_btn.config(state=DISABLED)
    for id in tiles[4].find_all():
        tiles[4].tag_bind(id, '<Button-1>', post_play)

def end_game(score):
    info_btn.grid_remove()
    disc_btn.grid_remove()
    play_btn.grid_remove()
    for tile in tiles:
        tile.grid_remove()
    main_text.set('Game Over')
    firework.aux(root, score)

if __name__=='__main__':
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((IP,PORT))
    d1 = loads(conn.recv(1024))
    player_num = d1['player num']
    data = unpack(d1)
    main_text.set('Waiting for your turn...')

    t = threading.Thread(target=data_thread, args=(conn,player_num))
    t.start()

    # Create board layout (columns, rows, color)
    board = [
            (1,2,'#653000'), #0 Board
            (1,4,'#653000'), #1 Board
            (0,1,'#1F1F1F'), #2 Hint
            (2,1,'#1F1F1F'), #3 Fuses
            (1,5,'#1F1F1F'), #4 Player 1
            (0,4,'#1F1F1F'), #5 Player 2
            (0,3,'#1F1F1F'), #6 Player 3
            (0,2,'#1F1F1F'), #7 Player 4
            (1,1,'#1F1F1F'), #8 Player 5
            (2,2,'#1F1F1F'), #9 Player 6
            (2,3,'#1F1F1F'), #X Player 7
            (2,4,'#1F1F1F'), #E Player 8
            ]
    tiles = [Canvas(root, bg='#653000', width=296, height=180, highlightthickness=0)]
    tiles[0].grid(column=1, row=2, rowspan=2)
    for x, y, color in board[1:]:
        tiles.append(Canvas(root, bg=f'{color}', width=296, height=90, highlightthickness=0))
        tiles[-1].grid(column=x,row=y)

    draw_status()
    draw_hands()
    draw_played()
    accessories()

    state = 'normal' if player_num == current_player else 'disabled'

    # Create gameplay buttons
    info_btn = Button(root, text='INFO', command=pre_info, padx=40, pady=12, state=state)
    info_btn.grid(column=0,row=6,sticky=N+S+E+W)
    disc_btn = Button(root, text='DISC', command=pre_discard, padx=40, pady=12, state=state)
    disc_btn.grid(column=1,row=6,sticky=N+S+E+W)
    play_btn = Button(root, text='PLAY', command=pre_play, padx=40, pady=12, state=state)
    play_btn.grid(column=2,row=6,sticky=N+S+E+W)

    # show window
    root.mainloop()


# CUTS

# tasks = [
# '''
# Task List
# ___________________________
# INFO                    (Y)
# -Choose player          (Y)
# -Choose information     (Y)
# DISCARD                 (Y)
# -Choose card            (Y)
# -Add to discard         (Y)
# -Draw card              (Y)
# PLAY                    (Y)
# -Choose card            (Y)
# -Check valid            (Y)
# --Add to play           (Y)
# --Add to discard        (Y)
# ---Loose a fuse         (Y)
# -Draw card              (Y)
# NETWORKING              (Y)
# -Server                 (Y)
# --Initalize             (Y)
# --Current player        (Y)
# --Echo                  (Y)
# -Client                 (Y)
# --Receive data          (Y)
# --Send data             (Y)
# MISC                    (Y)
# -Draw hints/fuses       (Y)
#     from data           (Y)
# -Final round            (Y)
# --If deck is empty      (Y)
#     add to counter      (Y)
# BUNDLE
# -App
# -Exe
# ''']

# '''
#     0   1   2
# 1 | H | 5 | F |
# 2 | 4 | B | 6 |
# 3 | 3 | B | 7 |
# 4 | 2 | B | 8 |
# 5 |   | 1 |   |
# 6 | I | D | P |
# '''

# # player1
# player1 = Canvas(root, height=90, width=320, bg='white', highlightthickness=0)
# player1.grid(column=1,row=4)
# # player2
# player2 = Canvas(root, height=90, width=320, bg='white', highlightthickness=0)
# player2.grid(column=0,row=3)
# # player3
# player3 = Canvas(root, height=90, width=320, bg='white', highlightthickness=0)
# player3.grid(column=0,row=1)
# # player4
# player4 = Canvas(root, height=90, width=320, bg='white', highlightthickness=0)
# player4.grid(column=1,row=0)
# # player5
# player5 = Canvas(root, height=90, width=320, bg='white', highlightthickness=0)
# player5.grid(column=2,row=1)
# # player6
# player6 = Canvas(root, height=90, width=320, bg='white', highlightthickness=0)
# player6.grid(column=2,row=3)
# # buttons
# buttons = Canvas(root, height=90, width=320, bg='green', highlightthickness=0)
# buttons.grid(column=1,row=5)
# # fuses
# fuses = Canvas(root, height=90, width=320, bg='blue', highlightthickness=0)
# fuses.grid(column=2,row=5)
# # hints
# hints = Canvas(root, height=90, width=320, bg='red', highlightthickness=0)
# hints.grid(column=0,row=5)
# screen1 = Canvas(root, height=300, width=300, bg='#152496', confine=True)
# screen1.grid(column=0, row=0, columnspan=3)
# screen2 = Canvas(frame, height=100, width=200, bg='#961524', confine=True, bd=0)
# screen2.grid(column=1, row=0)
# screen3 = Canvas(frame, height=100, width=200, bg='#249615', confine=True, bd=0)
# screen3.grid(column=2, row=0)

# tiles[5].create_rectangle(0,0,55,89, fill='white', activefill='black')
# tiles[5].create_rectangle(22,0,77,89, fill='white', activefill='black')
# tiles[5].create_rectangle(44,0,99,89, fill='white', activefill='black')
# tiles[5].create_rectangle(66,0,121,89, fill='white', activefill='black')
# tiles[5].create_rectangle(88,0,143,89, fill='white', activefill='black')

#
# # '''
# btnFrame = Frame(root, height=89, width=144)
# buttonLabels = ['Info', 'Dump', 'Play']
# buttons = [Button(btnFrame, text=f'{label}', highlightthickness=0) for label in buttonLabels]
# for i, button in enumerate(buttons):
#     button.grid(column=i,row=0)
# btnFrame.grid(column=1,row=5)
# '''


# tBtn = Button(root, text='Tell', command=lambda: print('1'))
# dBtn = Button(root, text='Dump', command=lambda: print('2'))
# pBtn = Button(root, text='Play', command=lambda: print('3'))
#
# tBtn.pack()
# dBtn.pack()
# pBtn.pack()

# tiles[1].create_rectangle(25,17,114,72, fill='white', outline='black', activefill='black', activeoutline='white')
# tiles[1].create_rectangle(178,17,267,72,fill='white', outline='black', activefill='black', activeoutline='white')

# tile.create_rectangle(val,0,val+55,89, fill='white', activefill='black', activeoutline='white')

# titleBar.pack(side='top',fill='x')
# frame.grid(column=0, row=0, columnspan=3)
# mainLbl = Label(root, width=100, textvariable=mainText, bg='#474747', fg='#FFFFFF', highlightthickness=0)
# mainLbl.grid(column=0, row=0, columnspan=3)

# tiles[0].create_rectangle(val1,val2,val1+55,val2+89,fill='white')

# for j in range(5):
#     for i in range(5):
#         val1 = 55*i + 10
#         val2 = 20*j + 10
#         options = {'fill':'white', 'outline':'black', 'smooth':True}
#         tiles[0].create_polygon(round_rectangle(val1,val2,val1+55,val2+89,radius=13), options)

# tiles[1].create_polygon(round_rectangle(25,17,114,72,radius=13), options)
# tiles[1].create_polygon(round_rectangle(178,17,267,72,radius=13), options)

# for tile in tiles[-6:]:
#     for k in range(5):
#         val = k*22 + 76
#         options = {'fill':'white', 'outline':'black', 'activefill':'black', 'activeoutline':'white', 'smooth':True}
        # tile.create_polygon(round_rectangle(val,0,val+55,89,radius=13), options)

# [Card(tiles[4], pos=[k*30 + 76, 0], show=[False, False]) for k in range(4)]
# [Card(tiles[4], pos=[k*22 + 76, 0], show=[False, False]) for k in range(5)]

# [[False, False], [False, False], [False, False], [False, False]],
# [[False, False], [False, False], [False, False], [False, False]],
# [[False, False], [False, False], [False, False], [False, False]],
# [[False, False], [False, False], [False, False], [False, False]],
# [[False, False], [False, False], [False, False], [False, False]],
# [[False, False] for _ in range(4)],

# data = {
#     'player info' : (True, 3, 3), # is current player, player number, total players
#     'title' : 'Welcome to Hanabi! Waiting for more players.',
#     'fuses' : [True, True, True, True],
#     'hints' : [True, True, True, True, True, True, True, True],
#     'deck' : {
#         'magenta': [1,1,1,2,2,3,3,4,4,5],
#         'yellow': [1,1,1,2,2,3,3,4,4,5],
#         'green': [1,1,1,2,2,3,3,4,4,5],
#         'blue': [1,1,1,2,2,3,3,4,4,5],
#         'red': [1,1,1,2,2,3,3,4,4,5],
#         },
#     'discard' : {
#         'magenta': [],
#         'yellow': [],
#         'green': [],
#         'blue': [],
#         'red': [],
#         },
#     'played' : {
#         'magenta': [],
#         'yellow': [],
#         'green': [],
#         'blue': [],
#         'red': [],
#         },
#     'known' : [
#             [[True, True], [True, True], [True, True], [True, True], [True, True]],
#             [[True, False], [True, False], [True, False], [True, False], [True, False]],
#             [[False, True], [False, True], [False, True], [False, True], [False, True]],
#             [[False, False], [False, False], [False, False], [False, False], [False, False]],
#             ],
#     'hands' : [
#         [f'magenta {i+1}' for i in range(5)],
#         [f'yellow {i+1}'  for i in range(5)],
#         [f'green {i+1}'   for i in range(5)],
#         [f'blue {i+1}'    for i in range(4)],
#         [f'red {i+1}'     for i in range(4)],
#         ]
#     }

# info = 'magenta' if XX<=x<=XX and YY<=y<=YY else
# for card, known in zip(self.players[d1-1].hand,self.players[d1-1].known):
#     if card.split()[d2] == data:
#         known[d2] = True

# # Create Hints and Fuses
# for x in range(4):
#     # Create hints
#     tiles[2].create_oval(x*60+10, 10, x*60+44, 44, fill='#0000F0', outline='#1F1F1F', tags=f'hint{2*x+0}')
#     tiles[2].create_oval(x*60+40, 44, x*60+74, 78, fill='#0000F0', outline='#1F1F1F', tags=f'hint{2*x+1}')
#     # Create fuses
#     tiles[3].create_oval(x*66+32, 28, x*66+66, 62, fill=fuse_colors[x], outline='#1F1F1F', tags=f'fuse{x}')

# # Create board layout (columns, rows, color)
# board = [
#         (1,2,'#653000'), # Board
#         (1,4,'#653000'), # Board
#         (0,1,'#1F1F1F'), # Hint
#         (2,1,'#1F1F1F'), # Fuses
#         (1,5,'#1F1F1F'), # Player 1
#         (0,4,'#1F1F1F'), # Player 2
#         (0,3,'#1F1F1F'), # Player 3
#         (0,2,'#1F1F1F'), # Player 4
#         (1,1,'#1F1F1F'), # Player 5
#         (2,2,'#1F1F1F'), # Player 6
#         (2,3,'#1F1F1F'), # Player 7
#         (2,4,'#1F1F1F'), # Player 8
#         ]
# tiles = [Canvas(root, bg='#653000', width=296, height=180, highlightthickness=0)]
# tiles[0].grid(column=1, row=2, rowspan=2)
# for x, y, color in board[1:]:
#     tiles.append(Canvas(root, bg=f'{color}', width=296, height=90, highlightthickness=0))
#     tiles[-1].grid(column=x,row=y)

# for x in range(4):
    # # Create hints
    # tiles[2].create_oval(x*60+10, 10, x*60+44, 44, fill='#0000F0', outline='#1F1F1F', tags=f'hint{2*x+0}')
    # tiles[2].create_oval(x*60+40, 44, x*60+74, 78, fill='#0000F0', outline='#1F1F1F', tags=f'hint{2*x+1}')
    # Create fuses
    # tiles[3].create_oval(x*66+32, 28, x*66+66, 62, fill=fuse_colors[x], outline='#1F1F1F', tags=f'fuse{x}')

    # #XXX
    # d1 = loads(hb.d1)
    # player_num = d1['player num']
    # data = unpack(d1)
    # #XXX
