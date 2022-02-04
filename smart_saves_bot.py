import telebot
import config
from telebot import types
from linkpreview import link_preview

bot=telebot.TeleBot(config.TOKEN)

@bot.message_handler(content_types=['text'])
def link_preview_parsing(message):
    if message.chat.type=='private' and (message.text[:8]=='https://' or message.text[:7]=='http://'):
        bot.send_message(message.chat.id, link_preview(message.text).description)
    else:
        bot.send_message(message.chat.id, '0')
bot.polling(none_stop=True)