# gtranslatebot-telegram
A Google Translate bot for Telegram

## Version
Python 3.6

## Configuration
Firstly, create a `telegram_token` file with the token for the bot in
the directory of this README-file.
Secondly, acquire a google service account key, download the
accompanying JSON-file, put it in the directory of this README-file,
and rename it to `google_app_credentials.json`.

### Setting up a virtualenv and installing deps
Run `virtualenv -p python3 venv && source venv/bin/activate && pip install -r requirements.txt`

### New deps
After installing new deps, run `pip freeze > requirements.txt`

## Running
`source venv/bin/activate` to activate the virtualenv.<br>
`./main.py` to run the script.
