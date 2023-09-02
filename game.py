from enum import Enum
from typing import List
from treys.treys import Evaluator
from treys.treys import Card as TreysCard

evaluator = Evaluator()


class PokerHand(Enum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class Card:
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
    SUITS = ['♠️', '♣️', '♦️', '♥️']

    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        FACE_CARDS = {'11': 'J', '12': 'Q', '13': 'K', '14': 'A'}
        rank = FACE_CARDS.get(self.rank, self.rank)
        return f'{rank}{self.suit}'

    def format_for_treys(self):
        TREYS_RANKS: str = '23456789TJQKA'
        TREYS_SUITS: str = 'scdh'

        rank_idx = self.RANKS.index(self.rank)
        suit_ids = self.SUITS.index(self.suit)

        treys_rank = TREYS_RANKS[rank_idx]
        treys_suit = TREYS_SUITS[suit_ids]

        return treys_rank + treys_suit

    def to_dict(self):
        return {
            'rank': self.rank,
            'suit': self.suit,
        }

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in Card.RANKS for suit in Card.SUITS]
        random.shuffle(self.cards)

    def deal(self, num_cards: int) -> List[Card]:
        dealt_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return dealt_cards


class Player:
    def __init__(self, telegram_id: str, name: str, chips: int = 500):
        self.telegram_id = telegram_id
        self.chips = chips  # Starting chips
        self.hole_cards: List[Card] = []
        self.current_bet = 0
        self.name = name
        self.has_called = False
        self.has_folded = False

    def bet(self, amount: int):
        if amount > self.chips:
            raise ValueError('Not enough chips to bet.')
        self.chips -= amount
        self.current_bet += amount

    # todo: you are here, fix this and check if player data is saved, also keep name, then it shouod send private msg with cards
    # check if cardas are ok or not
    def to_dict(self):
        return {
            'name': self.name,
            'chips': self.chips,
            'current_bet': self.current_bet,
            'hole_cards': [card.to_dict() for card in self.hole_cards],
            'telegram_id': self.telegram_id,
        }
    def fold(self):
        self.hole_cards = []
        self.current_bet = 0
        self.has_folded = True

    @classmethod
    def from_dict(cls, player_data):
        player = cls(player_data['telegram_id'], player_data['name'])
        player.chips = player_data['chips']
        player.current_bet = player_data['current_bet']
        player.hole_cards = [Card.from_dict(card_data) for card_data in player_data['hole_cards']]
        return player


import random


# Update the PokerGame class to include the deck and the dealing logic
class PokerGame:
    def __init__(self):
        self.starting_chips: int = 0  # Starting chips for each player
        self.players: List[Player] = []  # List of players in the game
        self.starting_state: List[Player] = []  # List of players in the game
        self.deck = Deck()
        self.current_bet = 0  # The current bet amount that players need to match
        self.last_action = None  # 'Check', 'Bet', 'Raise', 'Call', 'Fold'
        self.current_round = None  # 'Pre-flop', 'Flop', 'Turn', 'River'
        self.dealer: Player = None  # Player designated as the dealer
        self.small_blind = 0  # Amount of the small blind
        self.big_blind = 0  # Amount of the big blind
        self.pot = 0  # Total amount in the pot
        self.community_cards: List[Card] = []  # List of community cards
        self.current_stage = 'Initialization'  # Current stage of the game
        self.current_player = None  # Current player whose turn it is
        self.winner: Player = None  # Winner of the game
        self.loser: Player = None  # Loser of the game
        self.chat_id: str = None  # Chat ID of the game

    def add_player(self, player: Player):
        self.players.append(player)

    def start_game(self):
        # if dealer is empty set first user as dealer, if not set next user as dealer
        if not self.dealer:
            self.dealer = self.players[0]
        else:
            self.dealer = self.players[self.players.index(self.dealer) + 1]

        for player in self.players:
            player.hole_cards = self.deck.deal(2)
        self.current_round = 'Pre-flop'

    def handle_reset(self):
        # resets game state
        for player in self.players:
            # todo: reset to starting state
            pass

    def handle_blinds(self):
        # specifically casino poker rules
        self.players[0].has_called = True
        self.players[1].has_called = True
        # Handle blind logic
        self.players[0].chips -= self.small_blind
        self.players[1].chips -= 2 * self.small_blind
        self.players[0].current_bet = self.small_blind
        self.players[1].current_bet = 2 * self.small_blind
        self.pot += 3 * self.small_blind
        self.last_action = 'Blinds'
        self.current_bet = 2 * self.small_blind
        pass

    def handle_bet(self, player: Player, amount: int):
        if amount > player.chips:
            raise ValueError('Not enough chips to bet.')
        player.bet(amount)
        self.pot += amount
        self.current_bet += amount
        self.last_action = 'Bet'

    def handle_raise(self, player: Player, amount: int):
        if amount < self.current_bet or amount > player.chips:
            raise ValueError('Invalid raise amount.')
        player.bet(amount)
        self.pot += amount
        self.current_bet += amount
        self.last_action = 'Raise'

    def handle_call(self, player: Player):
        amount_to_call = self.current_bet - player.current_bet
        if amount_to_call > player.chips:
            raise ValueError('Not enough chips to call.')
        player.bet(amount_to_call)
        self.pot += amount_to_call
        self.last_action = 'Call'

    def handle_check(self, player: Player):
        if self.current_bet != player.current_bet:
            raise ValueError('Cannot check. Need to match the current bet.')
        self.last_action = 'Check'

    def handle_fold(self, player: Player):
        player.fold()
        # End the game if a player folds, and award the pot to the other player
        other_player = [p for p in self.players if p != player][0]
        other_player.chips += self.pot
        self.pot = 0
        self.last_action = 'Fold'

    # def handle_show(self):

    def next_round(self):
        if self.current_round == 'Pre-flop':
            self.community_cards.extend(self.deck.deal(3))
            self.current_round = 'Flop'
        elif self.current_round == 'Flop':
            print('Flop')
            self.community_cards.extend(self.deck.deal(2))
            self.winner, self.loser = self.end_game()
            self.current_round = 'End'
        #     # self.current_round = 'Turn & River'
        # elif self.current_round == 'Turn & River':
        #     print('Turn & River')
        #     self.community_cards.extend(self.deck.deal(2))
        #     self.winner = self.end_game()
        #     self.current_round = 'End'
        elif self.current_round == 'Turn':
            self.community_cards.extend(self.deck.deal(1))
            self.current_round = 'River'
        else:
            # print('Else end game')
            # self.winner = self.end_game()
            # self.current_round = 'End'
            pass

    def evaluate_winner(self):
        print('Evaluating winner')
        player1_hand_rank = HandEvaluator.evaluate_hand(self.players[0].hole_cards, self.community_cards)
        player2_hand_rank = HandEvaluator.evaluate_hand(self.players[1].hole_cards, self.community_cards)
        # Compare hand ranks
        if player1_hand_rank < player2_hand_rank:
            return self.players[0]
        elif player1_hand_rank > player2_hand_rank:
            return self.players[1]
        else:
            # If hand ranks are the same, compare key cards
            return None

    def to_dict(self) -> dict:
        """Convert the game state to a dictionary."""
        return {
            'players': [player.to_dict() for player in self.players],
            'dealer': self.dealer.to_dict() if self.dealer else None,
            'small_blind': self.small_blind,
            'big_blind': self.big_blind,
            'pot': self.pot,
            'community_cards': [card.to_dict() for card in self.community_cards],
            'current_stage': self.current_stage
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PokerGame':
        """Create a PokerGame instance from a dictionary."""
        game = cls()
        game.players = [Player.from_dict(player_data) for player_data in data['players']]
        game.dealer = Player.from_dict(data['dealer']) if data['dealer'] else None
        game.small_blind = data['small_blind']
        game.big_blind = data['big_blind']
        game.pot = data['pot']
        game.community_cards = [Card.from_dict(card_data) for card_data in data['community_cards']]
        game.current_stage = data['current_stage']
        return game

    def end_game(self):
        # Handle game end logic
        # check if only a single player is left
        if len([p for p in self.players if not p.has_folded]) == 1:
            # award the pot to the player
            player = [p for p in self.players if not p.has_folded][0]
            player.chips += self.pot
            self.pot = 0
            self.last_action = 'End'
            return player, [p for p in self.players if p.has_folded][0]
        else:
            winner = self.evaluate_winner()
            if winner:
                winner.chips += self.pot
                self.pot = 0
                self.last_action = 'End'
                return winner, self.players[1] if winner == self.players[0] else self.players[0]
            else:
                # split the pot
                for player in self.players:
                    player.chips += self.pot / len(self.players)
                self.pot = 0
                self.last_action = 'End'
                return None, None


from itertools import combinations


class HandEvaluator:
    @staticmethod
    def evaluate_hand(hand: List[Card], board: List[Card]) -> int:
        hand = [TreysCard.new(card.format_for_treys()) for card in hand]
        board = [TreysCard.new(card.format_for_treys()) for card in board]
        rank = evaluator.evaluate(hand, board)
        return rank

    @staticmethod
    def evaluate_rank_class(rank: int) -> str:
        return evaluator.class_to_string(evaluator.get_rank_class(rank))


def test_poker_game():
    board1 = Card('10', '♥️')
    board2 = Card('11', '♥️')
    board3 = Card('12', '♥️')
    board4 = Card('13', '♥️')
    board5 = Card('3', '♠️')

    starter1 = Card('12', '♠️')
    starter2 = Card('9', '♥️')

    joiner1 = Card('8', '♥️')
    joiner2 = Card('14', '♣️')

    free = Card('14', '♥️')

    player1 = Player('123', 'Player 1')
    player2 = Player('456', 'Player 2')

    game = PokerGame()
    game.add_player(player1)
    game.add_player(player2)

    # Test evaluate_hand
    rank = HandEvaluator.evaluate_hand([board1, board2, board3], [board4, free])
    # assert hand[0] == PokerHand.ROYAL_FLUSH, "evaluate_hand failed"
    print(HandEvaluator.evaluate_rank_class(rank))

    # Test evaluate_winner
    player1.hole_cards = [starter1, starter2]
    player2.hole_cards = [joiner1, joiner2]
    game.community_cards = [board1, board2, board3, board4, board5]
    winner = game.evaluate_winner()
    assert winner == player1, "evaluate_winner failed"
    print('we are all good')


# Run the test
test_poker_game()
