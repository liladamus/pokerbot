# Import necessary libraries and modules
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# Import auxiliary files (assuming they exist)
# import game_logic
# import api_calls

# Initialize the bot
TOKEN = '6439633643:AAHoE8tfyjt9gOfJJacWn4nKMxzSZ570RYs'
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the Poker Bot!")

def handle_message(update, context):
    # Handle incoming messages and commands
    # This is just a placeholder and should be expanded based on game logic and interactions
    pass

def test_bot(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Test successful! The bot is working.")

# Add a handler for the test command
test_handler = CommandHandler('test', test_bot)
dispatcher.add_handler(test_handler)


# Add handlers for commands and messages
start_handler = CommandHandler('start', start)
message_handler = MessageHandler(Filters.text & ~Filters.command, handle_message)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(message_handler)

# Start the bot
updater.start_polling()
updater.idle()