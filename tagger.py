'''AUTOTAGER OF MESSAGES'''

import database

# finds out which tags from database are passing to the text
# gets string of data
# returns array ['tag2', 'tag4' ...]
def get_tags(text):
    try:
        # dictionary formatted {'tag1':['keyword1', 'keyword2'], 
        #                       'tag2':['keyword3', 'keyword2'] ...} 
        if database.tags != {}:
            tags=database.tags
        else:
            raise Exception
        # what function returns
        valid_tags=[]

        # searching for valid tags
        for tag in tags:
            for keyword in tags[tag]:
                if (keyword in text) and (tag not in valid_tags):
                    valid_tags.append(tag)           
        return valid_tags
    except Exception as e:
        print(repr(e), 'tagger')

# formats list of tags into string with hashtags
# gets list of tags ['tag2', 'tag4' ...]
# returns string '#tag2 #tag4 ...' or ''
def format_tags(tags_list):
    if tags_list != []:
        formated_tags = '#'+' #'.join(tags_list)
        return formated_tags
    else:
        return ''