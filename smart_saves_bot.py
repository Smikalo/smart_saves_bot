import telebot
import linkpreview
import config
import database
from telebot import types
from linkpreview import link_preview

bot = telebot.TeleBot(config.TOKEN)

tags_db = database.db


@bot.message_handler(commands=['setup'])
def setup(message):

    bot.send_message(message.chat.id, tags_db)


@bot.message_handler(content_types=['text'])
def link_preview_parsing(message):
    try:
        text = message.text
        link_data = link_preview(message.text)
        if message.chat.type == 'private' and (text[:8] == 'https://' or text[:7] == 'http://') and text.count('\n') == 0:
            title = link_data.title
            description = link_data.description

            data = (title+'\n'+description).lower()

            correct_tags = [(i*(sum([(j in data) for j in tags_db[i]]) > 0)) for i in tags_db]
            if '' in correct_tags:
                correct_tags.remove('')

            tags = '#'+' #'.join(correct_tags)

            bot.send_message(message.chat.id, text+'\n'+tags)
        else:
            bot.send_message(message.chat.id, 'Message is not a single link.')
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Link is unreadable for some reason. Please tag it manually.')


bot.polling(none_stop=True)