'''UI'''

# getting essential libraries
from turtle import speed
import telebot
import config
import database
import tagger
import messages
from linkpreview import link_preview
from telebot import types

# if mode is 'manual', all users' messages are writen in new_tags
mode='!manual'

posting_speed='!fast'

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

@bot.message_handler(commands=['start'])
def setup(message):
    if message.chat.type == 'group':
        database.add('chats', message.chat.title.lower(), str(message.chat.id))
        database.add('tags', message.chat.title.lower(), message.chat.title.lower())
        bot.send_message(message.chat.id, messages.started+message.chat.title.lower())

@bot.message_handler(commands=['delete'])
def setup(message):
    if message.chat.type == 'group':
        database.delete(str(message.chat.title.lower()))
        bot.send_message(message.chat.id, messages.deleted+message.chat.title.lower())


@bot.message_handler(commands=['setup'])
def setup(message):
    if message.chat.type == 'group':
        bot.send_message(message.chat.id, messages.setup_message)


@bot.message_handler(commands=['fast'])
def add_key(message):
    global posting_speed
    if message.chat.type == 'private':
        posting_speed='fast'
        bot.send_message(message.chat.id, messages.fast)

@bot.message_handler(commands=['slow'])
def add_key(message):
    global posting_speed
    if message.chat.type == 'private':
        posting_speed='!fast'
        bot.send_message(message.chat.id, messages.not_so_fast)

@bot.message_handler(commands=['key'])
def key(message):
    if message.chat.type == 'group':
        bot.send_message(message.chat.id, messages.current_key_message+
                        '\n'+', '.join(database.get('tags',message.chat.title.lower(),'*'))+
                        '\n'+messages.change_message)

@bot.message_handler(commands=['change'])
def change(message):
    if message.chat.type == 'group':
        bot.send_message(message.chat.id, messages.changing_key_message)

@bot.message_handler(commands=['newkey'])
def new_key(message):
    global mode
    if message.chat.type == 'group':
        mode='newkey'

@bot.message_handler(commands=['addkey'])
def add_key(message):
    global mode
    if message.chat.type == 'group':
        mode='addkey'

# working with messages
@bot.message_handler(content_types=['text'])
def return_tagged_text(message):
    # using some globals to add 'manual' mode
    global TEXT,new_tags,mode,tags_list,tags_str

    if message.chat.type == 'private':
        try:
            # if you are just sending bot messages
            if mode == '!manual':
                # setting some usefull shortings
                TEXT = message.text
                chat = message.chat.id

                # if text is a single link
                if ('\n' not in TEXT) and (('https://' == TEXT[:8]) or ('http://' == TEXT[:7])):
                    # getting texts' link preview info
                    title = link_preview(TEXT).title
                    description = link_preview(TEXT).description
                    
                    # formating preview info
                    preview_TEXT = str(title)+'\n'+str(description)
                    data = preview_TEXT.lower()
                    
                # if text is not a link
                else:
                    data = TEXT.lower()

                # getting tags from data and formating them
                
                    
                tags_list = tagger.get_tags(data)
                tags_str = tagger.format_tags(tags_list)

                # forming request
                request = TEXT+messages.between_text_and_tags+tags_str

                if posting_speed == '!fast':
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
                elif posting_speed == 'fast':
                    bot.send_message(chat, request)
                    chats=database.get_chats()

                    # sending tagged message to corresponding chats
                    for tag in chats:
                        if tag in tags_list:
                            chat_id = chats[tag]
                            post_text=TEXT+messages.between_text_and_tags+tags_str
                            bot.send_message(chat_id, post_text)
                

            # if you want rewrite bots' tags
            elif mode == 'manual':
                new_tags=message.text
        
        except Exception as e:
            print(repr(e),'bot')
    
    elif mode == 'newkey':
        database.write('tags',message.chat.title.lower(),(message.text.lower()).split(' '))
        bot.send_message(message.chat.id, messages.changed_key_message+'\n'+', '.join(database.get('tags',message.chat.title.lower(),'*')))
        mode='!manual'
    
    elif mode == 'addkey':
        extended_tags=database.get('tags',message.chat.title.lower(),'*')
        extended_tags.extend((message.text.lower()).split(' '))
        database.write('tags',message.chat.title.lower(), extended_tags)
        bot.send_message(message.chat.id, messages.changed_key_message+'\n'+', '.join(database.get('tags',message.chat.title.lower(),'*')))
        mode='!manual'


# working with callbacks and buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_buttons(call):
    # globals are needed for 'manual' mode
    global mode, new_tags, tags_str, tags_list, TEXT
    try:
        if call.message:
            # if user'd like to send message tagged by bot straight to channels
            if call.data == 'OK':
                # useful shorting
                # once database will be introduce chats' IDs will be stored there (?)
                chats=database.get_chats()

                post_text=TEXT+messages.between_text_and_tags+'#none'

                
                # sending tagged message to corresponding chats
                for tag in chats:
                    if tag in tags_list:
                        chat_id = chats[tag]
                        post_text=TEXT+messages.between_text_and_tags+tags_str
                        bot.send_message(chat_id, post_text)
                
                # deleting buttons under the message
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=post_text, reply_markup=None)
                if post_text.count('#none')==0:
                    # sending message to insure user that everything worked out
                    bot.send_message(call.message.chat.id, messages.inform_about_posting)
                else:
                    bot.send_message(call.message.chat.id, messages.link_error)

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
                chats=database.get_chats()

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
