from argparse import ArgumentDefaultsHelpFormatter
import itertools
from random import shuffle
from time import sleep
import sys
from tracemalloc import stop


def pause():
    sleep(0.5)


class Card:
    card_values = {'Ace': [1, 11], '2': [2], '3': [3],'4': [4],
                '5': [5], '6': [6], '7': [7], '8': [8], '9': [9],
                '10': [10], 'Jack': [10], 'Queen': [10], 'King': [10]}
    suits = ['Spades', 'Diamonds', 'Clubs', 'Hearts']

    def __init__(self, face, suit):
        if face not in self.card_values.keys():
            raise ValueError(f"'{face}' is not a valid face value")
        if suit not in self.suits:
            raise ValueError(f"'{suit}' is not a valid suit value")
        self.face = face
        self.value = self.card_values[face]
        self.suit = suit

    def __str__(self):
        return f"{self.face} of {self.suit}"

    def __repr__(self):
        return self.__str__()


class Deck:
    def __init__(self):
        self.deck = []
        for face in Card.card_values.keys():
            for suit in Card.suits:
                self.deck.append(Card(face, suit))
        shuffle(self.deck)
    
    def draw(self):
        if len(self.deck) == 0:
            return None
        return self.deck.pop()


class Player:
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.bet = 0
        self.wins = 0
        self.loses = 0
        self.ties = 0
        self.hand = list()
        self.hand_totals = set()

    def add_to_hand(self, card):
        self.hand.append(card)
        self.hand_totals = self.get_hand_totals()

    def get_hand_totals(self):
        hand_totals = set()
        card_values = [card.value for card in self.hand]  # Values for each card in hand. 
        combinations = list(itertools.product(*card_values))
        for combination in combinations:
            hand_totals.add(sum(combination))
        return hand_totals

    def is_bust(self):
        if min(self.hand_totals) > 21:
            return True
        return False
    
    def hand_is_blackjack(self):
        return max(self.get_qualifying_hand_totals()) == 21 \
        and len(self.hand) == 2

    def get_qualifying_hand_totals(self):
        hand_totals_copy = self.hand_totals.copy()         
        for total in self.hand_totals:
            if total > 21:
                hand_totals_copy.remove(total)
        return hand_totals_copy

    def __lt__(self, other):
        return max(self.get_qualifying_hand_totals()) < \
            max(other.get_qualifying_hand_totals())

    def __gt__(self, other):
        return max(self.get_qualifying_hand_totals()) > \
            max(other.get_qualifying_hand_totals())

    def __eq__(self, other):
        if len(self.hand) == 0:
            return id(self) == id(other)
        return max(self.get_qualifying_hand_totals()) == \
            max(other.get_qualifying_hand_totals())


class Game:
    def __init__(self):
        self.deck = Deck()
        self.starting_chips = 0
        self.players = []
        self.dealer = Player("Dealer", 0)

    def ask_for_number_of_players(self):
        number_of_players = 0  
        while not (1 <= number_of_players <= 7):
            number_of_players = self.get_valid_int(
                "Please enter number of players. Must be between 1 and 7:\n"
                )
        return number_of_players

    def ask_players_for_hit(self):
        for player in self.players.copy():
            # Ask player for hit until turn ends.
            move = None
            while move != "S" and not player.is_bust():
                hand_totals = player.get_qualifying_hand_totals()
                # Display hand.
                print(f"Dealer has: {self.dealer.hand[0]}")
                print(f"{player.name} your hand is: ", end="")
                print(*player.hand, sep=", ")
                # Display hand value(s).
                print(f"Your hand value is: ", end="")
                print(*hand_totals, sep=", ")

                move = self.get_valid_move()
                if move == "H":
                    player.add_to_hand(self.deck.draw())
                    # Check if bust
                    if player.is_bust():
                        print(
                            f"Player{player.name} got {min(player.hand_totals)}! " +
                            "You went bust!"
                            )
                        print(f"{player.name} has ${player.chips} remaining.")
                        self.player_loses(player)

    def ask_to_play_again(self):
        # Ask to play another round
        play_again = input("Play another round? [Y/N]\n").upper().strip()
        if play_again == "N":
            print()
            for player in self.players:
                print(f"{player.name} leaves with ${player.chips}! Well done!")
            print("Thanks for playing!")
            sys.exit()

    def check_players_win_tie_loss(self, player):
        for player in self.players:
            if self.dealer.is_bust():
                if not player.is_bust():
                    self.player_wins(player)
            # Check if dealer has blackjack.
            elif self.dealer.hand_is_blackjack():
                if player.hand_is_blackjack():
                    self.player_ties()
                else:
                    self.player_loses()
            else:
                if player.hand_is_blackjack():
                    self.player_wins_blackjack()
                elif player > self.dealer:
                    self.player_wins(player)
                elif player == self.dealer:
                    self.player_ties(player)
                else:
                    self.player_loses(player)

    def deal_starting_hand(self):
        # Deal 2 cards each, one at a time, starting from player 1  to dealer
        for _ in range(2):
            for player in self.players:
                card = self.deck.draw()
                player.add_to_hand(card)
            # Dealer gets one card.
            self.dealer.add_to_hand(self.deck.draw())

    def dealer_algorithm(self):
        # Algorithm the dealer follows. Dealer stands on 17 or more.
        stand = False
        while not stand and not self.dealer.is_bust():
            # Draw
            card = self.deck.draw()
            print(f"Dealer draws {card}")
            self.dealer.add_to_hand(card)
            print("Hand totals: ", self.dealer.hand_totals)
            # Check if stand condition met.
            if max(self.dealer.get_qualifying_hand_totals()) >= 17:
                stand = True
                if self.dealer.is_bust():
                    print("Dealer bust!")
                else:
                    hand_total = max(self.dealer.get_qualifying_hand_totals())
                    print(f"Dealer stands on {hand_total}")

    def get_player_bets(self):
        # Retrieves a valid bet from all players.
        for player in self.players:
            valid_bet = False
            while not valid_bet:
                player.bet = self.get_valid_int("\n" +
                    f"{player.name}, enter an integer to place your bet amount.\n" +
                    f"You currently have ${player.chips} chips.\n" +
                    "Enter 0 if you would like to exit game.\n"
                )
                valid_bet = player.chips >= player.bet

    def get_players(self, number_of_players):
        # Initialises all Player() instances with their name and starting chips.
        for i in range(1, number_of_players + 1):
            player_name = input(f"Player {i}, what is your name?\n")
            self.players.append(Player(player_name, self.starting_chips))

    def get_valid_int(self, message):
        # Request a valid integer from a player until given.
        valid_type = False
        while not valid_type:
            number = input(message).strip()
            try:
                number = int(number)
                return number
            except:
                print("Please enter an integer")
    
    def get_valid_move(self):
        # Request a valid move from a player until given.
            valid_move = False
            while not valid_move: 
                move = input(
                    'Enter "H" to hit or "S" to stand:\n'
                    ).strip().upper()
                valid_move = move == "H" or move == "S"
            return move

    def player_loses(self, player):
        # Updates a players stats if loses.
        player.chips -= player.bet
        player.loses += 1
        print(f"You lost ${player.bet}! You have ${player.chips} chips remaining.")

    def player_ties(self, player):
        # Updates a players stats if ties. 
        player.ties += 1
        print(f"You tied! Your chips remain the same. \
            You have ${player.chips} chips remaining.")

    def player_wins(self, player):
        # Updates a players stats if wins.
        player.chips += player.bet
        player.wins += 1
        print(f"You won ${player.bet}! You have ${player.chips} chips remaining.")
    
    def player_wins_blackjack(self, player):
        # Updates a players stats if wins blackjack.
        winnings = player.bet * 1.5
        player.chips += winnings
        player.wins += 1
        print(f"You won ${winnings}! You have ${player.chips} chips remaining.")
            
    def remove_non_betters(self):
        # Removes players from the game if they bet 0.
        players_to_remove = []
        for player in self.players:
            # Check for players to remove.
            if player.bet == 0:
                players_to_remove.append(player)
        
        for player in players_to_remove:
            self.players.remove(player)

        # TODO: Below required if self.players.remove() does not compare object ids.
        # for i in range(len(self.players)-1, 0, -1):
        #     # Remove players from self.players
        #     if self.players[i] in players_to_remove:
        #         self.players.pop(i)

    def reset_game(self):
        # Resets the conditions required for each player
        # to start a new round.
        for player in self.players:
            player.hand = list()
            player.hand_totals = set()
            self.deck = Deck()

    def run(self):
        # Main function that runs the game.
        number_of_players = self.ask_for_number_of_players()
        self.starting_chips = self.get_valid_int(
            "Please enter starting chips:\n")
        self.get_players(number_of_players)  # Get player names.

        while True:
            self.reset_game()
            self.get_player_bets()
            # breakpoint()
            self.remove_non_betters()
            self.deal_starting_hand()
            print(f"Dealer has a {self.dealer.hand[0]}\n")
            self.ask_players_for_hit()
            self.dealer_algorithm()
            self.check_players_win_tie_loss()
            self.ask_to_play_again()


if __name__ == "__main__":
    Game().run()
