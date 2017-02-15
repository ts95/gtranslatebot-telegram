#!/usr/bin/env python3
#
# Google Translate Bot for Telegram
#
# @author  Toni Sucic
# @date    14.02.2017

import telebot
import json
import re
import os

from pathlib import Path
from google.cloud import translate

if not Path('telegram_token').is_file():
    raise Exception("No telegram_token file found.")

with open('telegram_token') as f:
    global token
    token = f.read().strip()

if not 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
    raise Exception("Lacking GOOGLE_APPLICATION_CREDENTIALS env variable.")

bot = telebot.TeleBot(token)
client = translate.Client()

print("Running Google Translate Bot...")

def reply_message_has_text(message):
    return message.reply_to_message != None and \
            message.reply_to_message.text != None

def report_error(message, error):
    error_msg = "Error: " + str(error)
    print(error_msg)
    bot.reply_to(message, error_msg)

def langcode_to_name(langcode):
    names = list(filter(lambda lang: lang['language'] == langcode,
            client.get_languages()))
    if len(names) == 0:
        raise Exception("This langcode is invalid.")
    return names[0]['name']

@bot.message_handler(commands=['start'])
def send_start(message):
    bot.reply_to(message, "Google Translate Bot started. Use /help for help.")

@bot.message_handler(commands=['help'])
def send_help(message):
    lines = [
        "Reply to a message with */translate* or *translate this* to translate it.",
        "Reply to a message with e.g. *en -> fr* to translate it into French from English and so on.",
        "Reply to a message with *detect lang* or *detect language* to detect the language of the message.",
        "\n",
        "Write e.g. *en -> fr: text here* to translate \"text here\" into French from English and so on.",
        "Write */translate text here* to translate \"text here\" into English (the language will be detected automatically).",
        "\n",
        "Tip: \"to\" can be used as a substitute for \"->\", since it's easier to type on mobile devices.",
    ]
    help_message = '\n'.join(lines)
    bot.reply_to(message, help_message, parse_mode='markdown')

@bot.message_handler(regexp=r'^\/translate (.+)')
def send_translation_with_arg(message):
    m = re.match(r'^\/translate (?P<text>.+)', message.text)
    text = m.group('text')

    try:
        result = client.translate(text)
        print(result)
        translated_text = result['translatedText']
        bot.reply_to(message, translated_text)
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
        print(result)
        translated_text = result['translatedText']
        bot.reply_to(reply_message, translated_text)
    except Exception as e:
        report_error(message, e)

@bot.message_handler(regexp=r'^\w{2} (->|to) \w{2}$')
def send_custom_translation(message):
    if not reply_message_has_text(message):
        return

    reply_message = message.reply_to_message

    m = re.match(r'^(?P<source>\w{2}) (->|to) (?P<target>\w{2})', message.text)
    source = m.group('source')
    target = m.group('target')

    try:
        result = client.translate(reply_message.text, source_language=source,
                target_language=target)
        print(result)
        translated_text = result['translatedText']
        bot.reply_to(reply_message, translated_text)
    except Exception as e:
        report_error(message, e)

@bot.message_handler(regexp=r'^\w{2} (->|to) \w{2}:\s{1,2}[^$]+')
def send_custom_translation_inline(message):
    regexp = r'^(?P<source>\w{2}) (->|to) (?P<target>\w{2}):\s{1,2}(?P<text>[^$]+)'
    m = re.match(regexp, message.text)
    source = m.group('source')
    target = m.group('target')
    text = m.group('text')

    try:
        result = client.translate(text, source_language=source,
                target_language=target)
        print(result)
        translated_text = result['translatedText']
        bot.reply_to(message, translated_text)
    except Exception as e:
        report_error(message, e)

@bot.message_handler(regexp=r'^detect lang(uage)?$')
def send_detection(message):
    if not reply_message_has_text(message):
        return

    reply_message = message.reply_to_message

    try:
        result = client.detect_language(reply_message.text)
        text = langcode_to_name(result['language']) + ' detected.'
        bot.reply_to(reply_message, text)
    except Exception as e:
        report_error(message, e)

bot.polling(none_stop=True)

