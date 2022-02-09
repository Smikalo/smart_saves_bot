'''STORES AND GIVES ACCESS TO USERS DATA'''
import sqlite3
conn = sqlite3.connect('smart_saves.db',check_same_thread=False)
c = conn.cursor()
'''
c.execute("""CREATE TABLE tags (
    tag text,
    keys text
)""")
c.execute("""CREATE TABLE chats (
    title text,
    id text
)""")
conn.commit()
'''
def add(table, column, data):
    if type(data)==type([]):
        s=' '.join(data)
    else:
        s=str(data)
    c.execute(f"INSERT INTO {table} VALUES ('{column}','{s}')")
    
    conn.commit()

#database.get('tags',message.chat.title.lower()),'*')

def get(table, column, data_id):
    if table == 'tags':
        c.execute(f"SELECT * FROM {table} WHERE tag = '{column}'")
        items=c.fetchall()
        if data_id=='*':
            print(items)
            ans=items[0][1].split(' ')
        else:
            ans=items[0][1].split(' ')[int(data_id)]
    else:
        c.execute(f"SELECT * FROM {table} WHERE title = '{column}'")
        items=c.fetchall()
        ans=items[0][1]
    
    conn.commit()
    return ans

#database.write('tags',message.chat.title.lower(),(message.text.lower()).split(' '))

def write(table, column, data):
    if table == 'tags':
        c.execute(f"SELECT * FROM {table} WHERE tag = '{column}'")
    else:
        c.execute(f"SELECT * FROM {table} WHERE title = '{column}'")
    items=c.fetchall()

    if items!=[]:
        if type(data)==type([]):
            s=' '.join(data)
        else:
            s=str(data)

    if table == 'tags':
        c.execute(f"""UPDATE {table} SET keys = '{s}' WHERE tag = '{column}'""")
    else:
        c.execute(f"""UPDATE {table} SET id = '{s}' WHERE title = '{column}'""")
    
    conn.commit()

#database.delete(message.chat.id)
def delete(chat):
    c.execute(f"DELETE from tags WHERE tag = '{chat}'")
    c.execute(f"DELETE from CHATS WHERE title = '{chat}'")
    conn.commit()
    
#database.CHATS
def get_chats():
    ans={}
    c.execute("SELECT * FROM CHATS")
    items=c.fetchall()
    for row in items:
        ans[row[0]]=row[1]
    conn.commit()    
    return ans

def get_Tags():
    ans={}
    c.execute("SELECT * FROM tags")
    items=c.fetchall()
    for row in items:
        ans[row[0]]=row[1].split(' ')
    conn.commit()  
    return ans
'''
def main():
    c.execute("SELECT * FROM tags")
    it=c.fetchall()
    for i in it:
        print(i)
    conn.commit() 

main()
'''
conn.commit()




'''
tags = {
    'coding': ['python', 'programmer'],
    'physics': ['physics', 'einstein']
}

CHATS={}


'''