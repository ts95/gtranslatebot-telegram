# gtranslatebot-telegram
A Google Translate bot for Telegram

## Version
Python 3.6

## Configuration
Firstly create a `telegram_token` file with the token for the bot.
Secondly acquire a google service account key, and download the
accompanying JSON-file. Create a `GOOGLE_APPLICATION_CREDENTIALS`
environment variable that points to the location of said JSON-file.

## Running
Run `source gtranslatebot/bin/activate` to activate the virtualenv.
Run `python3 main.py` to run the script.

