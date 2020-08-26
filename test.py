import datetime
import threading
import time
import sqlite3
import DataBase as db




def check_today_schedule_change(peer_id):  # Проверка если расписание изминилось на сегодня
    connection = sqlite3.connect('AGPU_Schedule_Bot_DB.db')
    cursor = connection.cursor()

    def get_send_updates_status_one(peed_id):
        cursor.execute("SELECT send_updates FROM Chats WHERE chat_id=?", (peed_id,))
        result = bool(list(cursor.fetchone())[0])
        return result

    while get_send_updates_status_one(peer_id):
        print("!!!!!")
        time.sleep(1)

def start_scan(*args):
    thread = threading.Thread(target=check_today_schedule_change, args=args)
    thread.start()
    time.sleep(5)
database=db
thread=start_scan(68051119,database)