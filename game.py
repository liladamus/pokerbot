from enum import Enum
from typing import List, Tuple
# from hand import HandEvaluator
# Define card suits and ranks
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']


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
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    SUITS = ['♠', '♣', '♦', '♥']

    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f'{self.rank}{self.suit}'

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
    def __init__(self, telegram_id: str, name: str):
        self.telegram_id = telegram_id
        self.chips = 100  # Starting chips
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
        self.players: List[Player] = []  # List of players in the game
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

    def handle_bet(self, player: Player, amount: int):
        if amount > player.chips:
            raise ValueError('Not enough chips to bet.')
        player.bet(amount)
        self.pot += amount
        self.current_bet = amount
        self.last_action = 'Bet'

    def handle_raise(self, player: Player, amount: int):
        if amount < 2 * self.current_bet or amount > player.chips:
            raise ValueError('Invalid raise amount.')
        player.bet(amount)
        self.pot += amount
        self.current_bet = amount
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
        # TODO: Handle game end logic


    def next_round(self):
        if self.current_round == 'Pre-flop':
            self.community_cards.extend(self.deck.deal(3))
            self.current_round = 'Flop'
        elif self.current_round == 'Flop':
            self.community_cards.extend(self.deck.deal(1))
            self.current_round = 'Turn'
        elif self.current_round == 'Turn':
            self.community_cards.extend(self.deck.deal(1))
            self.current_round = 'River'
        else:
            self.winner = self.end_game()
            self.current_round = 'End'
            pass


    def evaluate_winner(self):
        player1_hand_rank, player1_key_cards = HandEvaluator.evaluate_hand(self.players[0].hole_cards + self.community_cards)
        player2_hand_rank, player2_key_cards = HandEvaluator.evaluate_hand(self.players[1].hole_cards + self.community_cards)

        # Compare hand ranks
        if player1_hand_rank.value > player2_hand_rank.value:
            return self.players[0]
        elif player1_hand_rank.value < player2_hand_rank.value:
            return self.players[1]
        else:
            # If hand ranks are the same, compare key cards
            for card1, card2 in zip(player1_key_cards, player2_key_cards):
                if Card.RANKS.index(card1) > Card.RANKS.index(card2):
                    return 'Player 1'
                elif Card.RANKS.index(card1) < Card.RANKS.index(card2):
                    return 'Player 2'

            # If key cards are the same, compare remaining cards
            remaining_cards1 = sorted(self.players[0].hole_cards + self.community_cards, key=lambda x: Card.RANKS.index(x[0]), reverse=True)
            remaining_cards2 = sorted(self.players[1].hole_cards + self.community_cards, key=lambda x: Card.RANKS.index(x[0]), reverse=True)
            for card1, card2 in zip(remaining_cards1, remaining_cards2):
                if Card.RANKS.index(card1[0]) > Card.RANKS.index(card2[0]):
                    return self.players[0]
                elif Card.RANKS.index(card1[0]) < Card.RANKS.index(card2[0]):
                    return self.players[1]

            # If all cards are the same, it's a tie
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
            return player
        else:
        # handle showdown, print both player cards and announce the winner
            winner = self.evaluate_winner()
            if winner:
                winner.chips += self.pot
                self.pot = 0
                self.last_action = 'End'
                return winner
            else:
                # split the pot
                for player in self.players:
                    player.chips += self.pot / len(self.players)
                self.pot = 0
                self.last_action = 'End'
                return None


class HandEvaluator:
    @staticmethod
    def evaluate_hand(cards: List[Card]) -> Tuple[PokerHand, List[str]]:
        # This method will evaluate the hand and return a tuple of the hand rank and the key cards
        if HandEvaluator.is_royal_flush(cards):
            return (PokerHand.ROYAL_FLUSH, [])
        elif HandEvaluator.is_straight_flush(cards):
            return (PokerHand.STRAIGHT_FLUSH, [max(cards, key=lambda card: Card.RANKS.index(card.rank)).rank])
        elif HandEvaluator.is_four_of_a_kind(cards):
            return (PokerHand.FOUR_OF_A_KIND, [max(cards, key=lambda card: Card.RANKS.index(card.rank)).rank])
        elif HandEvaluator.is_full_house(cards):
            return (PokerHand.FULL_HOUSE, [max(cards, key=lambda card: Card.RANKS.index(card.rank)).rank])
        elif HandEvaluator.is_flush(cards):
            return (PokerHand.FLUSH, [max(cards, key=lambda card: Card.RANKS.index(card.rank)).rank])
        elif HandEvaluator.is_straight(cards):
            return (PokerHand.STRAIGHT, [max(cards, key=lambda card: Card.RANKS.index(card.rank)).rank])
        elif HandEvaluator.is_three_of_a_kind(cards):
            return (PokerHand.THREE_OF_A_KIND, [max(cards, key=lambda card: Card.RANKS.index(card.rank)).rank])
        elif HandEvaluator.is_two_pair(cards):
            return (PokerHand.TWO_PAIR, [max(cards, key=lambda card: Card.RANKS.index(card.rank)).rank])
        elif HandEvaluator.is_one_pair(cards):
            return (PokerHand.ONE_PAIR, [max(cards, key=lambda card: Card.RANKS.index(card.rank)).rank])
        else:
            return (PokerHand.HIGH_CARD, [max(card.rank for card in cards)])


    @staticmethod
    def is_royal_flush(cards: List[Card]) -> bool:
        # Check if the cards form a royal flush
        values = [card.rank for card in cards]
        suits = [card.suit for card in cards]
        return set(values) == {'10', 'J', 'Q', 'K', 'A'} and len(set(suits)) == 1

    @staticmethod
    def is_straight_flush(cards: List[Card]) -> bool:
        # Check if the cards form a straight flush
        if len(set(card.suit for card in cards)) == 1:
            values = sorted(cards, key=lambda card: Card.RANKS.index(card.rank))
            for i in range(len(values) - 1):
                if Card.RANKS.index(values[i + 1].rank) - Card.RANKS.index(values[i].rank) != 1:
                    return False
            return True
        return False


    @staticmethod
    def is_four_of_a_kind(cards: List[Card]) -> bool:
        values = [card.rank for card in cards]
        return any(values.count(value) == 4 for value in set(values))


    @staticmethod
    def is_full_house(cards: List[Card]) -> bool:
        values = [card.rank for card in cards]
        unique_values = set(values)
        return any(values.count(value) == 3 for value in unique_values) and any(
            values.count(value) == 2 for value in unique_values)

    @staticmethod
    def is_flush(cards: List[Card]) -> bool:
        suits = [card.suit for card in cards]
        return len(set(suits)) == 1

    @staticmethod
    def is_straight(cards: List[Card]) -> bool:
        values = sorted(cards, key=lambda card: Card.RANKS.index(card.rank))
        for i in range(len(values) - 1):
            if Card.RANKS.index(values[i + 1].rank) - Card.RANKS.index(values[i].rank) != 1:
                return False
        return True

    @staticmethod
    def is_three_of_a_kind(cards: List[Card]) -> bool:
        values = [card.rank for card in cards]
        return any(values.count(value) == 3 for value in set(values))

    @staticmethod
    def is_two_pair(cards: List[Card]) -> bool:
        values = [card.rank for card in cards]
        return sum(1 for value in set(values) if values.count(value) == 2) == 2

    @staticmethod
    def is_one_pair(cards: List[Card]) -> bool:
        values = [card.rank for card in cards]
        return any(values.count(value) == 2 for value in set(values))


def test_poker_game_logic():
    # Test HandEvaluator methods
    assert HandEvaluator.is_flush([Card('A', '♠'), Card('K', '♠'), Card('Q', '♠'), Card('J', '♠'), Card('10', '♠')]) == True
    assert HandEvaluator.is_straight([Card('A', '♠'), Card('K', '♠'), Card('Q', '♠'), Card('J', '♠'), Card('10', '♠')]) == True
    assert HandEvaluator.is_four_of_a_kind([Card('A', '♠'), Card('A', '♣'), Card('A', '♦'), Card('A', '♥'), Card('10', '♠')]) == True
    assert HandEvaluator.is_full_house([Card('A', '♠'), Card('A', '♣'), Card('A', '♦'), Card('10', '♥'), Card('10', '♠')]) == True
    assert HandEvaluator.is_three_of_a_kind([Card('A', '♠'), Card('A', '♣'), Card('A', '♦'), Card('J', '♥'), Card('10', '♠')]) == True
    assert HandEvaluator.is_two_pair([Card('A', '♠'), Card('A', '♣'), Card('J', '♦'), Card('J', '♥'), Card('10', '♠')]) == True
    assert HandEvaluator.is_one_pair([Card('A', '♠'), Card('A', '♣'), Card('Q', '♦'), Card('J', '♥'), Card('10', '♠')]) == True

    # Test PokerGame winner evaluation
    game = PokerGame()
    game.player1_cards = [Card('A', '♠'), Card('K', '♠'), Card('Q', '♠'), Card('J', '♠'), Card('10', '♠')]
    game.player2_cards = [Card('A', '♣'), Card('K', '♣'), Card('Q', '♣'), Card('J', '♣'), Card('9', '♣')]
    assert game.evaluate_winner() == 'Player 1'

    game.player1_cards = [Card('A', '♠'), Card('A', '♣'), Card('A', '♦'), Card('A', '♥'), Card('10', '♠')]
    game.player2_cards = [Card('A', '♣'), Card('A', '♠'), Card('A', '♦'), Card('10', '♥'), Card('10', '♠')]
    assert game.evaluate_winner() == 'Player 1'

    game.player1_cards = [Card('A', '♠'), Card('A', '♣'), Card('J', '♦'), Card('J', '♥'), Card('10', '♠')]
    game.player2_cards = [Card('A', '♣'), Card('A', '♠'), Card('J', '♦'), Card('J', '♥'), Card('10', '♠')]
    assert game.evaluate_winner() == 'Tie'

    print('All tests passed!')
