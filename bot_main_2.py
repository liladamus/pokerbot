# Import necessary libraries and modules
from telegram import Bot, Update, error
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
# Import auxiliary files (assuming they exist)
# import game_logic
# import api_calls
from game import PokerGame, Player

# Initialize the bot
TOKEN = '6439633643:AAHoE8tfyjt9gOfJJacWn4nKMxzSZ570RYs'
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

import json
import os


class GameState:
    FILE_PATH = 'game_state.json'

    @classmethod
    def save_state(cls, game: PokerGame):
        """Save the current game state to a file."""
        with open(cls.FILE_PATH, 'w') as file:
            json.dump(game.to_dict(), file)

    @classmethod
    def load_state(cls) -> PokerGame:
        """Load the game state from a file and return a PokerGame instance."""
        if not os.path.exists(cls.FILE_PATH):
            return None
        with open(cls.FILE_PATH, 'r') as file:
            if os.stat(cls.FILE_PATH).st_size == 0:
                return None
            else:
                game_data = json.load(file)
        return PokerGame.from_dict(game_data)

    @classmethod
    def clear_state(cls):
        """Clear the saved game state."""
        if os.path.exists(cls.FILE_PATH):
            os.remove(cls.FILE_PATH)


class PokerBot:
    def __init__(self, token: str):
        self.updater = Updater(token=token)
        # self.game = GameState.load_state() or PokerGame()
        self.game = PokerGame()
        self._register_handlers()

    def log_game_state(self):
        GameState.save_state(self.game)
        print(self.game.to_dict())
        print('Game state saved.')

    def help(self, update: Update, context: CallbackContext):
        """Send a message explaining how to use the bot."""
        help_text = (
            "Welcome to Poker Bot! Here's how you can play:\n"
            "/pokerstart - Start a new poker game.\n"
            "/joinpoker - Join an existing poker game.\n"
            "/call - Call the current bet.\n"
            "/raise <amount> - Raise the bet by the specified amount.\n"
            "/fold - Fold your hand.\n"
            "/check - Check if it's your turn.\n"
            "/bet <amount> - Bet the specified amount.\n"
            "/show - Show your cards.\n"
            "/abort - Abort the current game (only the game initiator can do this).\n"
            "Have fun!"
        )
        update.message.reply_text(help_text)

    def _register_handlers(self):
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler('pokerstart', self.start_poker))
        dp.add_handler(CommandHandler('joinpoker', self.join_poker))
        dp.add_handler(CommandHandler('call', self.call_bet))
        dp.add_handler(CommandHandler('raise', self.raise_bet))
        dp.add_handler(CommandHandler('fold', self.fold))
        dp.add_handler(CommandHandler('check', self.check))
        dp.add_handler(CommandHandler('bet', self.place_bet))
        dp.add_handler(CommandHandler('show', self.show_cards))
        dp.add_handler(CommandHandler('abort', self.abort))
        dp.add_handler(CommandHandler('pokerhelp', self.help))
        dp.add_handler(CommandHandler('help', self.help))

    def abort(self, update: Update, context: CallbackContext):
        """Abort the current game."""
        user = update.message.from_user
        if user.id != self.game.players[0].id:
            update.message.reply_text('Only the initiator of the game can abort it.')
        else:
            update.message.reply_text('Game aborted.')
            GameState.clear_state()

    def inform_players(self):
        self.send_message(
            f"It is {self.game.current_player.name}'s turn. You have {self.game.current_player.chips} chips. The current bet is {self.game.current_bet} chips. The current pot is {self.game.pot} chips. use /call, /raise, /fold, /check, /bet to play your turn.")

    def start_poker(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        bet_amount = int(context.args[0]) if context.args else 0
        # Create a new Player object and add it to the game
        player = Player(user.id, user.username)
        self.game.add_player(player)
        # Store the chat_id of the game
        self.game.chat_id = update.message.chat_id
        update.message.reply_text(
            f'{user.first_name} has initiated a 1v1 poker game with a bet of {bet_amount} PVP tokens. other can join using /joinpoker')
        GameState.save_state(self.game)

    def join_poker(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        # Check if the user has already joined the game
        if any(player for player in self.game.players if player.telegram_id == user.id):
            update.message.reply_text(f'{user.first_name}, you have already joined the game!')
        else:
            # Create a new Player object and add it to the game
            player = Player(user.id, user.username)
            self.game.add_player(player)
            update.message.reply_text(f'{user.first_name} has joined the game! Setting up the table...')
            GameState.save_state(self.game)
            self.start_game()

    def send_message(self, message: str):
        """Send a message to the group chat."""
        self.updater.bot.send_message(chat_id=self.game.chat_id, text=message)

    def send_private_message(self, user_id: int, username: str, message: str):
        """Send a private message to a user."""
        try:
            self.updater.bot.send_message(chat_id=user_id, text=message)
        except error.Unauthorized:
            self.send_message(f"User {username} has not initiated a chat with the bot.")

    def start_game(self):
        # Check if there are two players in the game
        if len(self.game.players) != 2:
            print(self.game.to_dict())
            self.send_message("We need two players to start the game.")
            return

        # Start the game in the PokerGame class
        self.game.start_game()

        # Notify the group chat about the game start
        dealer_name = self.game.dealer.name
        other_player = [player for player in self.game.players if player != self.game.dealer][0]
        other_player_name = other_player.name
        self.send_message(
            f"{dealer_name} is the dealer for this round. {other_player_name} posts the small blind. {dealer_name} posts the big blind.")

        self.log_game_state()
        # Send private hole cards to each player
        for player in self.game.players:
            hole_cards = ", ".join([f"{card.rank}{card.suit}" for card in player.hole_cards])
            self.send_private_message(player.telegram_id, player.name, f"Your hole cards are: {hole_cards}")
        # set game'c current player to the player after the dealer
        self.game.current_player = self.game.players[
            (self.game.players.index(self.game.dealer) + 1) % len(self.game.players)]

        self.inform_players()

        # Print the current hand, deck, and game state to the console for debugging
        print("Current Hand:",
              [f"{card.rank}{card.suit}" for player in self.game.players for card in player.hole_cards])
        print("Current Deck:", [f"{card.rank}{card.suit}" for card in self.game.deck.cards])
        print("Current Game State:", self.game.to_dict())

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    def call_bet(self, update: Update, context: CallbackContext):
        try:
            user = update.message.from_user
            if not self.game or self.game.current_player.name != user.username:
                update.message.reply_text('It\'s not your turn.')
                return

            # Implement call logic
            self.game.handle_call(self.game.current_player)
            self.game.current_player.has_called = True
            update.message.reply_text(f'{user.first_name} calls.')
            GameState.save_state(self.game)
            self.next_player()
        except Exception as e:
            self.send_message(f"An error occurred: {str(e)}")

    def raise_bet(self, update: Update, context: CallbackContext):
        try:
            user = update.message.from_user
            if not self.game or self.game.current_player.name != user.username:
                update.message.reply_text('It\'s not your turn.')
                return

            amount = int(context.args[0]) if context.args else 0
            # Implement raise logic
            self.game.handle_raise(self.game.current_player, amount)
            # set has_called for all other players to False and for this player to True
            for player in self.game.players:
                player.has_called = False
            self.game.current_player.has_called = True
            update.message.reply_text(f'{user.first_name} raises by {amount} PVP tokens.')
            GameState.save_state(self.game)
            self.next_player()

        except Exception as e:
            self.send_message(f"An error occurred: {str(e)}")

    def fold(self, update: Update, context: CallbackContext):
        try:
            user = update.message.from_user
            if not self.game or self.game.current_player.name != user.username:
                update.message.reply_text('It\'s not your turn.')
                return

            # Implement fold logic
            self.game.handle_fold(self.game.current_player)
            self.game.current_player.has_folded = True
            update.message.reply_text(f'{user.first_name} folds.')
            GameState.save_state(self.game)
            self.next_player()
        except Exception as e:
            self.send_message(f"An error occurred: {str(e)}")

    def check(self, update: Update, context: CallbackContext):
        # try:
        user = update.message.from_user
        if not self.game or self.game.current_player.name != user.username:
            update.message.reply_text('It\'s not your turn.')
            return

        # Implement check logic
        self.game.handle_check(self.game.current_player)
        self.game.current_player.has_called = True
        update.message.reply_text(f'{user.first_name} checks.')
        GameState.save_state(self.game)
        self.next_player()
        # except Exception as e:
        #     self.send_message(f"An error occurred: {str(e)}")

    def place_bet(self, update: Update, context: CallbackContext):
        try:
            user = update.message.from_user
            if not self.game or self.game.current_player.name != user.username:
                update.message.reply_text('It\'s not your turn.')
                return

            amount = int(context.args[0]) if context.args else 0
            # Implement bet logic
            self.game.handle_bet(self.game.current_player, amount)
            # set has_called for all other players to False and for this player to True
            for player in self.game.players:
                player.has_called = False
            self.game.current_player.has_called = True
            update.message.reply_text(f'{user.first_name} bets {amount} PVP tokens.')
            GameState.save_state(self.game)
            self.next_player()

        except Exception as e:
            self.send_message(f"An error occurred: {str(e)}")

    def show_cards(self, update: Update, context: CallbackContext):
        try:
            user = update.message.from_user
            if not self.game or self.game.current_player.name != user.username:
                update.message.reply_text('It\'s not your turn.')
                return

            # Implement show cards logic
            cards = self.game.show_cards()
            update.message.reply_text(f'{user.first_name} shows {cards[0]} and {cards[1]}.')
            GameState.save_state(self.game)
        except Exception as e:
            self.send_message(f"An error occurred: {str(e)}")

    def next_player(self):
        # check if everybody has called or folded
        if self.game.current_player == self.game.dealer:
            # If all players have either called or folded, move to the next round
            if all(player.has_called or player.has_folded for player in self.game.players):
                self.game.next_round()
                # send the new cards to the players
                if self.game.current_round == 'End':
                    self.send_message(f" The game has ended. The winner is {self.game.winner.name}")
                    self.game = PokerGame()
                    return
                else:
                    self.send_message(
                        f" Round is {self.game.current_round}. The new cards are: {self.game.community_cards}")
                    # reset the players' has_called and has_folded attributes
                    for player in self.game.players:
                        player.has_called = False
                        player.has_folded = False
        # Move to the next player
        self.game.current_player = self.game.players[
            (self.game.players.index(self.game.current_player) + 1) % len(self.game.players)]

        self.inform_players()


# Uncomment the lines below to run the bot
# TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = PokerBot(TOKEN)
bot.run()