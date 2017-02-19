#!/usr/bin/env python3
#
# Google Translate Bot for Telegram
#
# @author  Toni Sucic
# @date    14.02.2017

import sys

if sys.version_info < (3, 6):
    raise Exception("This script requires Python 3.6 or higher.")

import telebot
import logging
import json
import html
import re
import os

from pathlib import Path
from google.cloud import translate

# The name of the bot on Telegram
BOT_NAME = 'gtranslatebot'

log = logging.getLogger('gtranslatebot.main')

if not Path('telegram_token').is_file():
    raise Exception("No telegram_token file found.")

with open('telegram_token') as f:
    global token
    token = f.read().strip()

if not Path('google_app_credentials.json').is_file():
    raise Exception("No google_app_credentials.json file found.")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_app_credentials.json'

bot = telebot.TeleBot(token)
client = translate.Client()

log.info("Running Google Translate Bot")

def reply_message_has_text(message):
    return message.reply_to_message != None and \
            message.reply_to_message.text != None

def report_error(message, error):
    error_msg = "Error: "

    if "Bad language pair" in str(error):
        error_msg += "bad language pair."
    elif "Invalid Value" in str(error):
        error_msg += "invalid language code. Write *code for [language]* to get the language code of a given language."
    else:
        error_msg += "an unknown error occured."

    log.error(str(error))
    bot.reply_to(message, error_msg, parse_mode='markdown')

def langcode_to_name(langcode):
    langs = client.get_languages()
    names = list(filter(lambda lang: lang['language'] == langcode, langs))
    if len(names) == 0:
        raise Exception("This langcode is invalid.")
    return names[0]['name']

@bot.message_handler(regexp=r'^\/start(@'+BOT_NAME+r')?$')
def send_start(message):
    bot.reply_to(message, "Google Translate Bot started. Use /help for help.")

@bot.message_handler(regexp=r'^\/help(@'+BOT_NAME+r')?$')
def send_help(message):
    lines = [
        "Reply to a message with */translate* or *translate this* to translate it.",
        "Reply to a message with e.g. *en -> fr* to translate it into French from English and so on.",
        "Reply to a message with *detect lang* or *detect language* to detect the language of the message.",
        "",
        "Write e.g. *en -> fr: text here* to translate _text here_ into French from English and so on.",
        "Write */translate text here* to translate _text here_ into English (the language will be detected automatically).",
        "Write *code for [language]* to get the language code for the language. e.g. *code for English*",
        "",
        "Tip: *to* can be used as a substitute for *->*, since it's easier to type on mobile devices.",
    ]
    help_message = '\n'.join(lines)
    bot.reply_to(message, help_message, parse_mode='markdown')

@bot.message_handler(regexp=r'^\/translate(@'+BOT_NAME+r')? (.+)')
def send_translation_with_arg(message):
    m = re.match(r'^\/translate(@\w+)? (?P<text>.+)', message.text)
    text = m.group('text')

    try:
        result = client.translate(text)
        log.info(result)
        translated_text = result['translatedText']
        bot.reply_to(message, html.unescape(translated_text))
    except Exception as e:
        report_error(message, e)

@bot.message_handler(commands=['translate'])
@bot.message_handler(regexp=r'^translate this$')
def send_translation(message):
    if not reply_message_has_text(message):
        return

    reply_message = message.reply_to_message

    try:
        result = client.translate(reply_message.text)
        log.info(result)
        translated_text = result['translatedText']
        bot.reply_to(reply_message, html.unescape(translated_text))
    except Exception as e:
        report_error(message, e)

@bot.message_handler(regexp=r'^\w{2,3}(-\w{2})? (->|to) \w{2,3}(-\w{2})?$')
def send_custom_translation(message):
    if not reply_message_has_text(message):
        return

    reply_message = message.reply_to_message

    m = re.match(r'^(?P<source>\w{2,3}(-\w{2})?) (->|to) (?P<target>\w{2,3}(-\w{2})?)', message.text)
    source = m.group('source')
    target = m.group('target')

    try:
        result = client.translate(reply_message.text, source_language=source, target_language=target)
        log.info(result)
        translated_text = result['translatedText']
        bot.reply_to(reply_message, html.unescape(translated_text))
    except Exception as e:
        report_error(message, e)

@bot.message_handler(regexp=r'^\w{2,3}(-\w{2})? (->|to) \w{2,3}(-\w{2})?:\s{1,2}[^$]+')
def send_custom_translation_inline(message):
    regexp = r'^(?P<source>\w{2,3}(-\w{2})?) (->|to) (?P<target>\w{2,3}(-\w{2})?):\s{1,2}(?P<text>[^$]+)'
    m = re.match(regexp, message.text)
    source = m.group('source')
    target = m.group('target')
    text = m.group('text')

    try:
        result = client.translate(text, source_language=source, target_language=target)
        log.info(result)
        translated_text = result['translatedText']
        bot.reply_to(message, html.unescape(translated_text))
    except Exception as e:
        report_error(message, e)

@bot.message_handler(regexp=r'^detect lang(uage)?$')
def send_detection(message):
    if not reply_message_has_text(message):
        return

    reply_message = message.reply_to_message

    try:
        result = client.detect_language(reply_message.text)
        name = langcode_to_name(result['language'])
        text = f"*{name}* detected."
        bot.reply_to(reply_message, text, parse_mode='markdown')
    except Exception as e:
        report_error(message, e)

@bot.message_handler(regexp=r'^code for \w+( [\(\)\w]+)?$')
def send_code_for_lang(message):
    m = re.match(r'^code for (?P<language>\w+( [\(\)\w]+)?)$', message.text)
    language = m.group('language')

    langs = client.get_languages()
    finds = list(filter(lambda lang: language.lower() in lang['name'].lower(), langs))

    if len(finds) == 0:
        bot.reply_to(message, "You either misspelled the language, or it's unsupported.")
    else:
        text = '\n'.join(map(lambda lang: lang['name'] + ': *' + lang['language'] + '*', finds))
        bot.reply_to(message, text, parse_mode='markdown')

@bot.message_handler(regexp=r'^\/getvalidlangcodes(@'+BOT_NAME+r')?$')
def send_valid_langcodes(message):
    langs = client.get_languages()
    text = '\n'.join(map(lambda lang: lang['name'] + ': *' + lang['language'] + '*', langs))
    bot.reply_to(message, text, parse_mode='markdown')

bot.polling(none_stop=True)
