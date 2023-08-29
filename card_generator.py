from PIL import Image
import os


class Card:
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    SUITS = ['♠️', '♣️', '♦️', '♥️']

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


def card_notation_to_file(card: Card):
    value = card.rank
    suit = card.suit

    if value == "A":
        value = "ace"
    elif value == "K":
        value = "king"
    elif value == "Q":
        value = "queen"
    elif value == "J":
        value = "jack"

    if suit == '♠️':
        suit = "spades"
    elif suit == '♥️':
        suit = "hearts"
    elif suit == '♦️':
        suit = "diamonds"
    elif suit == '♣️':
        suit = "clubs"
    else:
        raise ValueError("Invalid card suit")

    return f"{value}_of_{suit}.png"


def generate_card_image(cards):
    CARD_WIDTH = 100  # Adjust as per your images
    CARD_HEIGHT = 150  # Adjust as per your images

    result = Image.new("RGB", (CARD_WIDTH * len(cards), CARD_HEIGHT))

    for i, card in enumerate(cards):
        card_file = card_notation_to_file(str(card))
        card_image_path = os.path.join(os.getcwd(), "card-images",
                                       card_file)  # Assuming card images are in a folder named "card-images"
        image = Image.open(card_image_path)
        result.paste(image, (i * CARD_WIDTH, 0))

    return result
