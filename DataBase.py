import sqlite3

class Database:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_link_from_GroupsT(self, name):
        self.cursor.execute("SELECT group_link FROM Groups WHERE group_name=:nameKey", {'nameKey': name})
        return self.cursor.fetchone()[0]

    def group_name_is_in_DB(self, name):
        self.cursor.execute("SELECT EXISTS(SELECT group_link FROM Groups WHERE group_name=?)", (name,))
        s = list(self.cursor.fetchone())[0]
        return s

    def chat_id_is_in_DB(self, chat_id):
        self.cursor.execute("SELECT EXISTS(SELECT chat_id FROM Chats WHERE chat_id=:chat_idKey)",
                            {'chat_idKey': chat_id})
        result = list(self.cursor.fetchone())[0]
        return result

    def get_group_link_by_peer_id(self, peer_id):
        self.cursor.execute("SELECT group_link From Chats WHERE chat_id=:peer_idKey", {"peer_idKey": peer_id})
        result = list(self.cursor.fetchone())[0]
        return result

    def insert_to_chats_t(self, peer_id, group_name):
        group_link = self.get_link_from_GroupsT(group_name)[0]
        self.cursor.execute("INSERT INTO Chats (chat_id , group_link) VALUES (:peer_idKey,:group_linkKey)",
                            {"peer_idKey": peer_id, "group_linkKey": group_link})
        self.connection.commit()

    def update_to_chats_t(self, peer_id, group_name):
        group_link = self.get_link_from_GroupsT(group_name)
        self.cursor.execute("UPDATE Chats SET group_link = ? WHERE chat_id =?", (group_link, peer_id))
        self.connection.commit()

    def get_send_updates(self):
        self.cursor.execute("SELECT * FROM Chats WHERE send_updates=1")
        send_updates = self.cursor.fetchall()
        return send_updates

    def get_send_updates_status_one(self, peed_id):
        self.cursor.execute("SELECT send_updates FROM Chats WHERE chat_id=?", (peed_id,))
        result = bool(list(self.cursor.fetchone())[0])
        return result

    def set_last_lessons_by_peer_id(self, peer_id, day_lessons):
        self.cursor.execute("UPDATE Chats SET last_lessons = ? WHERE chat_id =?", (day_lessons, peer_id))
        self.connection.commit()

    def review_ChatsT(self, peer_id, group_name):
        if self.chat_id_is_in_DB(peer_id):
            self.update_to_chats_t(peer_id, group_name)
        else:
            self.insert_to_chats_t(peer_id, group_name)


#db = Database('AGPU_Schedule_Bot_DB.db')
#db.update_to_chats_t(68051119, "ВМ-ИВТ-3-1")
