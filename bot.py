import random
import logging
import requests
import telebot
from telebot.types import Message
from telebot import types

logging.basicConfig(filename="errors.log", level=logging.INFO)

TOKEN = '**********************************************'
STICKER_ID = 'CAADAgADBAADgqoRDwABPpw4HAMU2QI'


bot = telebot.TeleBot(TOKEN)
USERS = set()


keyboard = types.InlineKeyboardMarkup()
keyboard.add(types.InlineKeyboardButton(text="Random", callback_data="random"))
keyboard.add(types.InlineKeyboardButton(text="Joke", callback_data="joke"))


# button's calls


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "random":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=str(random.random()))
            logging.info("Button @random@ triggered")

        if call.data == "joke":
            logging.info("Button @joke@ triggered")
            r = requests.get('https://geek-jokes.sameerkumar.website/api')
            if r.raise_for_status():
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="No jokes for now, buddy")
                bot.send_sticker(call.message.chat.id, STICKER_ID)
                logging.error(f'Bad response: {r.json()}')
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=r.json())
                logging.info("Response for @joke@ button is ok")

    bot.send_message(call.message.chat.id, "Want joke or random number?", reply_markup=keyboard)


# reaction to commands


@bot.message_handler(commands=['start', 'random', 'joke', 'help'])
def command_handler(message: Message):
    if 'start' in message.text:
        bot.reply_to(message, 'Start command')
        logging.info("Command @start@ triggered")
    if 'random' in message.text:
        bot.reply_to(message, str(random.random()))
        logging.info("Command @random@ triggered")
    if 'joke' in message.text:
        logging.info("Command @joke@ triggered")
        r = requests.get('https://geek-jokes.sameerkumar.website/api')
        if r.raise_for_status():
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text="No jokes for now, buddy")
            bot.send_sticker(message.chat.id, STICKER_ID)
            logging.error(f'Bad response: {r.json()}')
        else:
            bot.reply_to(message, r.json())
            logging.info("Response for @joke@ command is ok")

    if 'help' in message.text:
        bot.reply_to(message, 'Help command')
        logging.info("Command @help@ triggered")
    bot.send_message(message.chat.id, "Want joke or random number?", reply_markup=keyboard)


# reaction to text


@bot.edited_message_handler(content_types=['text'])
@bot.message_handler(content_types=['text'])
def echo_text(message: Message):
    if message.from_user.id in USERS:
        bot.send_message(message.chat.id, "Want joke or random number?", reply_markup=keyboard)
    else:
        reply = f" Hello, {message.from_user.first_name}"
        reply += '\nI can only give you random number(0 - 1) or tell a joke about Chuck Norris\n'
        bot.send_message(message.chat.id, reply, reply_markup=keyboard)
    USERS.add(message.from_user.id)


# reaction to stickers


@bot.message_handler(content_types=['sticker'])
def sticker_handler(message: Message):
    bot.send_sticker(message.chat.id, message.sticker.file_id)
    bot.send_message(message.chat.id, "Want joke or random number?", reply_markup=keyboard)


bot.polling(none_stop=True)
