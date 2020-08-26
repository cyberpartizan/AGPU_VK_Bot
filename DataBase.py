import sqlite3

connection = sqlite3.connect('AGPU_Schedule_Bot_DB.db')
cursor = connection.cursor()


def get_link_from_GroupsT(name):
    cursor.execute("SELECT group_link FROM Groups WHERE group_name=:nameKey", {'nameKey': name})
    return cursor.fetchone()[0]


def group_name_is_in_DB(name):
    cursor.execute("SELECT EXISTS(SELECT group_link FROM Groups WHERE group_name=?)", (name,))
    s = list(cursor.fetchone())[0]
    return s


def chat_id_is_in_DB(chat_id):
    cursor.execute("SELECT EXISTS(SELECT chat_id FROM Chats WHERE chat_id=:chat_idKey)", {'chat_idKey': chat_id})
    result = list(cursor.fetchone())[0]
    return result


def get_group_link_by_peer_id(peer_id):
    cursor.execute("SELECT group_link From Chats WHERE chat_id=:peer_idKey", {"peer_idKey": peer_id})
    result = list(cursor.fetchone())[0]
    return result


def insert_to_ChatsT(peer_id, group_name):
    group_link = get_link_from_GroupsT(group_name)[0]
    cursor.execute("INSERT INTO Chats (chat_id , group_link) VALUES (:peer_idKey,:group_linkKey)",
                   {"peer_idKey": peer_id, "group_linkKey": group_link})
    connection.commit()


def update_to_ChatsT(peer_id, group_name):
    group_link = get_link_from_GroupsT(group_name)
    cursor.execute("UPDATE Chats SET group_link = ? WHERE chat_id =?", (group_link, peer_id))
    connection.commit()


def get_send_updates_status_one(peed_id):
    cursor.execute("SELECT send_updates FROM Chats WHERE chat_id=?",(peed_id,) )
    result = bool(list(cursor.fetchone())[0])
    return result

def get_send_updates_status_many():
    cursor.execute("SELECT * FROM Chats")
    send_updates=cursor.fetchall()
    return send_updates


def review_ChatsT(peer_id, group_name):
    if chat_id_is_in_DB(peer_id):
        update_to_ChatsT(peer_id, group_name)
    else:
        insert_to_ChatsT(peer_id, group_name)

#print(get_send_updates_status_many())
print(get_send_updates_status_one(68051119))