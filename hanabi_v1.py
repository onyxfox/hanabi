from colorama import Fore,Style
import random

# Set Player Number
try:
    numPlayers = int(input('How many players?\n'))
except ValueError:
    numPlayers = 4

# Initialize
deck = {
    'magenta': [1,1,1,2,2,3,3,4,4,5],
    'yellow': [1,1,1,2,2,3,3,4,4,5],
    'green': [1,1,1,2,2,3,3,4,4,5],
    'blue': [1,1,1,2,2,3,3,4,4,5],
    'red': [1,1,1,2,2,3,3,4,4,5],
    }

inPlay = {
    'magenta': [],
    'yellow': [],
    'green': [],
    'blue': [],
    'red': [],
    }

discard = {
    'magenta': [],
    'yellow': [],
    'green': [],
    'blue': [],
    'red': [],
    }

hints = [True, True, True, True, True, True, True, True]
fuses = [False, False, False, False]
score, count = 0, 0

# Switch Statements (Python does not have switch statements)
def mainSwitch(argument):
    switcher = {
        '1': 'GIVE INFO',
        '1.': 'GIVE INFO',
        '1. give information': 'GIVE INFO',
        'info': 'GIVE INFO',
        'information': 'GIVE INFO',
        'give info': 'GIVE INFO',
        'give information': 'GIVE INFO',
        '2': 'DISCARD',
        '2.': 'DISCARD',
        '2. discard': 'DISCARD',
        'discard': 'DISCARD',
        '3': 'PLAY',
        '3.': 'PLAY',
        'play': 'PLAY',
        '3. play': 'PLAY',
    }

    return(switcher.get(argument, "Invalid action. Please try again"))
def infoSwitch(argument):
    switcher = {'magenta':0,'yellow':0,'green':0,'blue':0,'red':0,'1':1,'2':1,'3':1,'4':1,'5':1}
    print(switcher.get(argument, None))
    return(switcher.get(argument, None))

# GUI
def gui():
    mag, magDis = inPlay.get('magenta',[]), discard.get('magenta',[])
    yel, yelDis = inPlay.get('yellow',[]) , discard.get('yellow',[])
    grn, grnDis = inPlay.get('green',[])  , discard.get('green',[])
    blu, bluDis = inPlay.get('blue',[])   , discard.get('blue',[])
    red, redDis = inPlay.get('red',[])    , discard.get('red',[])
    return(f'''

Hanabi
In Play:\t\tDiscard:
{Fore.MAGENTA}{mag}\t\t{magDis}{Style.RESET_ALL}
{Fore.YELLOW}{yel}\t\t{yelDis}{Style.RESET_ALL}
{Fore.GREEN}{grn}\t\t{grnDis}{Style.RESET_ALL}
{Fore.BLUE}{blu}\t\t{bluDis}{Style.RESET_ALL}
{Fore.RED}{red}\t\t{redDis}{Style.RESET_ALL}

Fuses: {sum([int(not fuse) for fuse in fuses])}
Hints: {sum([int(hint) for hint in hints])}

''')

# Horrible name but I can't think of anything else
# It changes hints and fuses based on number input
def changeState(num):
    # Negative number means use hint
    if num < 0:
        # print('Lost a hint')
        hints[hints.index(True)] = False
    # Positive number means gain hint
    elif num > 0:
        # print('Gained a hint')
        hints[hints.index(False)] = True
    # Zero means blew fuse
    else:
        # print('Lost a fuse')
        fuses[fuses.index(False)] = True

# Sets up player and methods
class Player:
    def __init__(self, num):
        self.hand = [self.draw(), self.draw(), self.draw(), self.draw()]
        self.known = [[False, False], [False, False], [False, False], [False, False]]
        self.number = num
        if numPlayers <= 3:
            self.hand.append(self.draw())
            self.known.append([False, False])

    def __repr__(self):
        return(f'Player({self.number})')

    def __str__(self):
        return('Player')

    def draw(self):
        # Get random card from deck
        color = random.choice(list(deck.keys()))
        while len(deck.get(color)) == 0:
            color = random.choice(list(deck.keys()))
        index = random.randint(0,len(deck.get(color))-1)
        # Add card to hand
        card = f'{color} {deck.get(color)[index]}'
        # Remove card from deck
        del deck.get(color)[index]
        # Return
        return(card)

    def info(self):
        # Check if any hints availible
        if not any(hints):
            print('\n\nYou can\'t give a hint. Try a different action.')
            self.gameplay()
        else:
            # Choose player
            try:
                s1 = int(input('Choose a player number\n'))
                if s1 <= 0:
                    print('Number too small. Try again.')
                    self.info()
                elif s1 > numPlayers - 1:
                    print('Number too large. Try again.')
                    self.info()
                else:
                    # Use hint
                    changeState(-1)
                    # Ask for info to give
                    test = input('What info do you want give?\n')
                    test = test.lower()
                    # Get index based on color or number
                    s2 = infoSwitch(test)
                    # Give info
                    for card,known in zip(players[s1-1].hand,players[s1-1].known):
                        if card.split()[s2] == test:
                            known[s2] = True
                        # print('gave info')
            except ValueError:
                self.info()

    def discard(self):
        if all(hints):
            print('\n\nYou can\'t discard. Try a different action.')
            self.gameplay()
        else:
            # Gain hint
            changeState(1)
            # Choose card
            idx = self.chooseCard() - 1
            # Add to discard
            card = self.hand[idx].split()
            discard[card[0]].append(int(card[1]))
            discard[card[0]].sort()
            # Add new card
            if any(deck.values()):
                self.hand[idx] = self.draw()
                self.known[idx] = [False, False]
            else:
                del self.hand[idx]
                del self.known[idx]

    def play(self):
        # Choose card
        idx = self.chooseCard() - 1
        card = self.hand[idx].split()
        # Get highest card
        try:
            val = inPlay[card[0]][-1]
        except IndexError:
            val = 0
        # Check if valid
        if val + 1 == int(card[1]):
            # Add to play
            inPlay[card[0]].append(int(card[1]))
            inPlay[card[0]].sort()
            # Add card to score
            global score
            score = score + int(card[1])
            # Add hint back if completing sequence
            if int(card[1]) == 5:
                changeState(1)
        else:
            # Add to discard
            discard[card[0]].append(int(card[1]))
            discard[card[0]].sort()
            # Use fuse
            changeState(0)
        # Draw card
        if any(deck.values()):
            self.hand[idx] = self.draw()
            self.known[idx] = [False, False]
        else:
            del self.hand[idx]
            del self.known[idx]

    def gameplay(self):
        print('What do you want to do?')
        print('1. Give Information (info)')
        print('2. Discard (discard)')
        print('3. Play (play)')
        s1 = mainSwitch(input().lower())
        if s1 == 'GIVE INFO':
            self.info()
        elif s1 == 'DISCARD':
            self.discard()
        elif s1 == 'PLAY':
            self.play()
        else:
            self.gameplay()

    def show(self):
        self.str = ''
        for card, val in zip(self.hand,self.known):
            color, num = card.split()
            col = self.foreColor(color)
            if val[0] & val[1]:
                self.str = f'{self.str} |{col}{num}{Style.RESET_ALL}|'
            elif val[0]:
                self.str = f'{self.str} |{col}*{Style.RESET_ALL}|'
            elif val[1]:
                self.str = f'{self.str} |{num}|'
            else:
                self.str = f'{self.str} |*|'
        return(f'{self.str}')

    def tell(self):
        tellStr = ''
        for card in self.hand:
            color, num = card.split()
            col = self.foreColor(color)
            tellStr = f'{tellStr} |{col}{num}{Style.RESET_ALL}|'
        return(f'{tellStr}')

    def chooseCard(self):
        try:
            num = int(input('Choose a card\n'))
        except ValueError:
            print('Please try again')
            num = self.chooseCard()
        if (numPlayers >= 4 & num > 4) | ((numPlayers < 4) & (num > 5)):
            print('Number too large')
            print('Please try again')
            num = self.chooseCard()
        elif num <= 0:
            print('Number to small. Try again')
            num = self.chooseCard()
        return num

    def foreColor(self,color):
        if color == 'magenta':
            return(Fore.MAGENTA)
        elif color == 'yellow':
            return(Fore.YELLOW)
        elif color == 'green':
            return(Fore.GREEN)
        elif color == 'blue':
            return(Fore.BLUE)
        elif color == 'red':
            return(Fore.RED)
        else:
            return(Fore.RESET)


# Check if main program running
if __name__ == '__main__':
    # Setup
    players = [Player(x+1) for x in range(numPlayers)]

    # Gameloop
    while True:
        # Get current player
        current = players.pop(0)

        # GUI
        print(gui())

        # Show Own Hand
        print(f'Your Hand:', end='    ')
        print(current.show(), end='')

        # Tell Other Players Hands
        for i, player in enumerate(players):
            print(f'Player {i+1} Turn:', end='')
            print(player.tell())

        # Gameplay starts
        print()
        current.gameplay()

        # Win or Lose Condition
        if all(fuses):
            # Lose Game
            print('\n\nYou Blew Up!')
            break
        elif score == 25:
            # Win Game
            print('\n\nYou Won!')
            break
        elif not any(deck.values()):
            # Empty Deck
            count =+ 1
            if count == numPlayers:
                break
            else:
                continue
        else:
            players.append(current)

    # Show score
    print(f'Game Finished!\nYou scored {score} points!')


# Unused Extras
#
# '''
# Server Steps
# (y) Ask number of players
# (y) Create players
# (y) When number connected equals number of players start game
# (y) Show game state (EVERYONE)
# (y) Show hands (PERSONAL)
# (y) Tell hands
# (y) Show game play(PERSONAL)
# (y) Get input from one player
# (y) Get next player
# (n) What to do if a player disconects
# '''
# print(f'\nHanabi')
# print(f'In Play:\t\tDiscard:')
# mag = inPlay.get('magenta',[])
# magDis = discard.get('magenta',[])
# print(f'{Fore.MAGENTA}{mag}\t\t{magDis}{Style.RESET_ALL}')
# yel = inPlay.get('yellow',[])
# yelDis = discard.get('yellow',[])
# print(f'{Fore.YELLOW}{yel}\t\t{yelDis}{Style.RESET_ALL}')
# grn = inPlay.get('green',[])
# grnDis = discard.get('green',[])
# print(f'{Fore.GREEN}{grn}\t\t{grnDis}{Style.RESET_ALL}')
# blu = inPlay.get('blue',[])
# bluDis = discard.get('blue',[])
# print(f'{Fore.BLUE}{blu}\t\t{bluDis}{Style.RESET_ALL}')
# red = inPlay.get('red',[])
# redDis = discard.get('red',[])
# print(f'{Fore.RED}{red}\t\t{redDis}{Style.RESET_ALL}')
# print()
# print(f'Fuses: {fuses}')
# print(f'Hints: {hints}')
# print()
#
# def playerSwitch(argument):
#     switcher = {'player 1': 1,
#         '1': 1,
#         '1.': 1,
#         'player 2': 2,
#         '2': 2,
#         '2.': 2,
#         'player 1': 1,
#             '1': 1,
#             '1.': 1,
#     }
#     return(switcher.get(argument, "Invalid action. Please try again"))
#
# for i, player in enumerate(players):
# for i in range(numPlayers):
# def setup():
#     player1 = Player()
#     for i in range(5):
#         player1.play()
#     print(inPlay)
#     print(discard)
#     print(players[x].hand)
# elif not any(deck.values()):
#     # Check if deck is empty
#     print('Last Round')
# elif all(hints) == False:
#     print('No Info')
# elif all(hints) == True:
#     print('No Discard')
#
# color_test = 'BLUE'
# print(f'{Fore.BLUE} ___________ {Style.RESET_ALL}')
# print(f'{Fore.BLUE}| * * * * * |{Style.RESET_ALL}')
# print(f'{Fore.BLUE}| * * * * * |{Style.RESET_ALL}')
# print(f'{Fore.BLUE}| * * * * * |{Style.RESET_ALL}')
# print(f'{Fore.BLUE}| * * * * * |{Style.RESET_ALL}')

# for i, player in enumerate(players):
# 	t = players.pop(i)
# 	print(players)
# 	players.insert(i,t)

        # print(f'''
        # Hanabi
        # Hints: [*****@@@]    Fuses: [XX00]
        #
        # Play:               DISCARD:
        # {Fore.MAGENTA}[1,2,3,4,5]         [1,2,3,4,5]{Style.RESET_ALL}
        # {Fore.YELLOW}[1,2,3,4,5]         [1,2,3,4,5]{Style.RESET_ALL}
        # {Fore.GREEN}[1,2,3,4,5]         [1,2,3,4,5]{Style.RESET_ALL}
        # {Fore.BLUE}[1,2,3,4,5]         [1,2,3,4,5]{Style.RESET_ALL}
        # {Fore.RED}[1,2,3,4,5]         [1,2,3,4,5]{Style.RESET_ALL}
        #
        # Player 1 Hand: |{Fore.MAGENTA}2{Style.RESET_ALL}| |{Fore.YELLOW}*{Style.RESET_ALL}| |{Fore.YELLOW}2{Style.RESET_ALL}| |{Fore.BLUE}*{Style.RESET_ALL}| |{Fore.RED}*{Style.RESET_ALL}|
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Player 2 Hand: |{Fore.GREEN}2{Style.RESET_ALL}| |{Fore.GREEN}2{Style.RESET_ALL}| |{Fore.BLUE}3{Style.RESET_ALL}| |{Fore.YELLOW}4{Style.RESET_ALL}| |{Fore.MAGENTA}1{Style.RESET_ALL}|
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Player 3 Hand: |{Fore.BLUE}2{Style.RESET_ALL}| |{Fore.BLUE}2{Style.RESET_ALL}| |{Fore.BLUE}3{Style.RESET_ALL}| |{Fore.GREEN}4{Style.RESET_ALL}| |{Fore.GREEN}1{Style.RESET_ALL}|
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Player 4 Hand: |{Fore.YELLOW}2{Style.RESET_ALL}| |{Fore.YELLOW}2{Style.RESET_ALL}| |{Fore.YELLOW}3{Style.RESET_ALL}| |{Fore.YELLOW}4{Style.RESET_ALL}| |{Fore.YELLOW}1{Style.RESET_ALL}|
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Player 5 Hand: |{Fore.MAGENTA}2{Style.RESET_ALL}| |{Fore.YELLOW}2{Style.RESET_ALL}| |{Fore.GREEN}3{Style.RESET_ALL}| |{Fore.BLUE}4{Style.RESET_ALL}| |{Fore.RED}1{Style.RESET_ALL}|
        # ''')
        # hand = print('|*| |*| |*| |*| |*|')
        # print(f'{Fore.RED}red{Style.RESET_ALL}')
        # print(f'{Fore.RED}red{Style.RESET_ALL}')
        # print(f'{Fore.GREEN}green{Style.RESET_ALL}')
        # print(f'{Fore.YELLOW}yellow{Style.RESET_ALL}')
        # print(f'{Fore.MAGENTA}magenta{Style.RESET_ALL}')
        # print(f'{Fore.BLUE}blue{Style.RESET_ALL}')


        # print('* *')

        # Show hands of players other then current one
        # current = players.pop(i)
        # for nonPlayer in players:
        #     nonPlayer.tell()
        # #     # nonPlayer.show()
        # # players.append(current)
        # players.insert(i, current)
