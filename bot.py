# getting essential libraries
import telebot
import config
import database
import tagger
import messages
from linkpreview import link_preview
from telebot import types

mode='!manual'
new_tags=''
# initialising bot
bot = telebot.TeleBot(config.TOKEN)

# working with commands
@bot.message_handler(commands=['setup'])
def setup(message):
    bot.send_message(message.chat.id, '/setup')



# working with messages
@bot.message_handler(content_types=['text'])
def return_tagged_text(message):
    global TEXT,new_tags,mode,tags_list,tags_str
    try:
        if mode != 'manual':
            # setting some usefull shortings
            TEXT = message.text
            chat = message.chat.id

            # if text is a single link
            if ('\n' not in TEXT) and (('https://' == TEXT[:8]) or ('http://' == TEXT[:7])):
                # getting texts' link preview info
                title = link_preview(TEXT).title
                description = link_preview(TEXT).description
                
                # formating preview info
                preview_TEXT = title+'\n'+description
                data = preview_TEXT.lower()
            # if text is not a link
            else:
                data = TEXT.lower()

            # getting tags from data and formating them
            tags_list = tagger.get_tags(data)
            tags_str = tagger.format_tags(tags_list)

            # forming request
            request = TEXT+messages.between_text_and_tags+tags_str

            # asking for users' approuval
                # creating two vote buttons under bots' message
            markup=types.InlineKeyboardMarkup(row_width=2)
            item1=types.InlineKeyboardButton('👍',callback_data='OK')
            item2=types.InlineKeyboardButton('👎',callback_data='REDO')
            markup.add(item1,item2)
                # sending bots' tags guess
            bot.send_message(chat, request, reply_markup=markup)
                # asking
            bot.send_message(chat, messages.tags_verification)
        else:
            new_tags=message.text

    except Exception as e:
        print(repr(e),'bot')


# working with callbacks and buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_buttons(call):
    global mode, new_tags, tags_str, tags_list
    try:
        if call.message:
            if call.data == 'OK':
                chats=config.CHATS
                for tag in chats:
                    if tag in tags_list:
                        chat_id = chats[tag]
                        post_text=TEXT+messages.between_text_and_tags+tags_str
                        bot.send_message(chat_id, post_text)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=post_text, reply_markup=None)
                bot.send_message(call.message.chat.id, messages.inform_about_posting)

            elif call.data == 'REDO':
                bot.send_message(call.message.chat.id, messages.tags_manual_mode_question)
                
                markup=types.InlineKeyboardMarkup(row_width=1)
                item=types.InlineKeyboardButton('✅',callback_data='DONE')
                markup.add(item)
                mode='manual'
                
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
            elif call.data == 'DONE':
                mode="!manual"
                new_text=TEXT+messages.between_text_and_tags+new_tags
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_text, reply_markup=None)
                
                new_tags_list=new_tags[1:].split(' #')
                
                chats=config.CHATS
                for tag in chats:
                    if tag in new_tags_list:
                        chat_id = chats[tag]
                        post_text=TEXT+messages.between_text_and_tags+new_tags
                        bot.send_message(chat_id, post_text)

                bot.send_message(call.message.chat.id, messages.inform_about_posting)
                
    except Exception as e:
        print(repr(e))


bot.polling(none_stop=True)