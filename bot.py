# getting essential libraries
import telebot
import config
import database
import tagger
import messages
from linkpreview import link_preview
from telebot import types

# if mode is 'manual', all users' messages are writen in new_tags
mode='!manual'

# if user does not like which tags bot used, he can go into 'manual' 
# mode and send new tags for message to the bot. Then, to confirm changes
# user needs to press a button under message he wants to retag
new_tags=''

# initialising bot
bot = telebot.TeleBot(config.TOKEN)

# working with commands
# /help - list of basic commands and functionalities
# /setup - setup mode, in which user can setup database information
# /status - current bot setuos
# /info - some info about bots' creator(optional)
@bot.message_handler(commands=['setup'])
def setup(message):
    bot.send_message(message.chat.id, '/setup')



# working with messages
@bot.message_handler(content_types=['text'])
def return_tagged_text(message):
    # using some globals to add 'manual' mode
    global TEXT,new_tags,mode,tags_list,tags_str
    try:
        # if you are just sending bot messages
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
                # creating two vote buttons under bots' message: '👍' and '👎'
            markup=types.InlineKeyboardMarkup(row_width=2)

                    # yes, post like this
            item1=types.InlineKeyboardButton('👍',callback_data='OK')
                    # no, I'd rather rewrite these tags manually
            item2=types.InlineKeyboardButton('👎',callback_data='REDO')

            markup.add(item1,item2)

                # sending bots' tags guess
            bot.send_message(chat, request, reply_markup=markup)
                # asking
            bot.send_message(chat, messages.tags_verification)
        # if you want rewrite bots' tags
        else:
            new_tags=message.text

    except Exception as e:
        print(repr(e),'bot')


# working with callbacks and buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_buttons(call):
    # globals are needed for 'manual' mode
    global mode, new_tags, tags_str, tags_list
    try:
        if call.message:
            # if user'd like to send message tagged by bot straight to channels
            if call.data == 'OK':
                # useful shorting
                # once database will be introduce chats' IDs will be stored there (?)
                chats=config.CHATS

                # sending tagged message to corresponding chats
                for tag in chats:
                    if tag in tags_list:
                        chat_id = chats[tag]
                        post_text=TEXT+messages.between_text_and_tags+tags_str
                        bot.send_message(chat_id, post_text)
                
                # deleting buttons under the message
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=post_text, reply_markup=None)
                # sending message to insure user that everything worked out
                bot.send_message(call.message.chat.id, messages.inform_about_posting)

            # if user'd like to write tags on his own
            elif call.data == 'REDO':
                # sending user instructions on how to rewrite tags
                bot.send_message(call.message.chat.id, messages.tags_manual_mode_question)
                # adding '✅' approuval button under message user wants to retag
                markup=types.InlineKeyboardMarkup(row_width=1)
                item=types.InlineKeyboardButton('✅',callback_data='DONE')
                markup.add(item)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)

                # setting mode to 'manual'
                # now message_handler sets new_tags variable to whatever user sends
                # until user types '✅' button under message
                mode='manual'

            # if user pressed '✅' button and wants to post retagged message
            elif call.data == 'DONE':
                # mode is normal again, message_handler works normally
                mode="!manual"
                # rewriting old message as user wants and deleting buttons under it
                new_text=TEXT+messages.between_text_and_tags+new_tags
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_text, reply_markup=None)
                
                # generating list of new tags that user gave 
                new_tags_list=new_tags[1:].split(' #')
                
                # useful shorting
                # once database will be introduce chats' IDs will be stored there (?)
                chats=config.CHATS

                # sending retagged message to corresponding chats
                for tag in chats:
                    if tag in new_tags_list:
                        chat_id = chats[tag]
                        post_text=TEXT+messages.between_text_and_tags+new_tags
                        bot.send_message(chat_id, post_text)

                # sending message to insure user that everything worked out
                bot.send_message(call.message.chat.id, messages.inform_about_posting)
                
    except Exception as e:
        print(repr(e))

# always welcome for new users' messages
bot.polling(none_stop=True)