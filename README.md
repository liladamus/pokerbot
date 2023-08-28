# Poker Bot

This project is a Telegram bot for playing 1v1 poker games. The bot manages the game state, deals cards, and handles user actions such as calling, raising, folding, and checking.

## Features

- Start a new poker game
- Join an existing poker game
- Call the current bet
- Raise the bet by a specified amount
- Fold your hand
- Check if it's your turn
- Bet a specified amount
- Show your cards
- Abort the current game (only the game initiator can do this)

## Usage

The bot responds to the following commands:

- `/pokerstart` - Start a new poker game.
- `/joinpoker` - Join an existing poker game.
- `/call` - Call the current bet.
- `/raise <amount>` - Raise the bet by the specified amount.
- `/fold` - Fold your hand.
- `/check` - Check if it's your turn.
- `/bet <amount>` - Bet the specified amount.
- `/show` - Show your cards.
- `/abort` - Abort the current game (only the game initiator can do this).
- `/pokerhelp` or `/help` - Get a list of all commands and their descriptions.

## Setup

1. Clone the repository
2. Install the necessary libraries with `pip install -r requirements.txt`
3. Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual Telegram bot token
4. Run the bot with `python bot.py`

## Dependencies

- Python 3.6+
- python-telegram-bot library

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT
