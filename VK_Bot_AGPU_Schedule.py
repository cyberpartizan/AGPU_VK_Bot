import datetime
import os
import socket
import threading
import time

import AGPU_Schedule_Parser as parser
import requests
import urllib3
import vk_api
from DataBase import Database
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
#6d3e7800807862b42f09c5b0adeb32c71d8646aef4e70ec1db414dba89d328d2e48e49486f2fdae46333d
# Импорт API ключа(токена)
API_KEY = os.environ.get("API_KEY")
#API_KEY = "6d3e7800807862b42f09c5b0adeb32c71d8646aef4e70ec1db414dba89d328d2e48e49486f2fdae46333d"
print("Бот работает...")
group_id = '197937466'  # Указываем id сообщества, изменять только здесь!
oshibka = 0  # обнуление счетчика ошибок
threads = []
db = Database('AGPU_Schedule_Bot_DB.db')
Start_thread=True
q=True
def main():
    global oshibka  # Счетчик ошибок
    try:
        vk_session = vk_api.VkApi(token=API_KEY)  # Авторизация под именем сообщества
        longpoll = VkBotLongPoll(vk_session, group_id)
        vk = vk_session.get_api()

        def send_msg(ms_g):
            vk.messages.send(peer_id=event.object.peer_id, random_id=0, message=ms_g)

        def send_msg_by_peer_id(ms_g, peer_id):
            vk.messages.send(peer_id=peer_id, random_id=0, message=ms_g)

        def check_today_lessons_update():  # Проверка на обновления расписания за день
            db_inthread = Database('AGPU_Schedule_Bot_DB.db')
            while True:
                while (datetime.datetime.now().hour >= 8) and (datetime.datetime.now().hour < 24):
                    chats = db_inthread.get_send_updates()
                    for chat in chats:
                        currentday = chat[3]
                        if currentday != parser.today(groupLink=chat[1]):
                            currentday = parser.today(groupLink=chat[1])
                            send_msg_by_peer_id("Расписание изменилась \n \n" + currentday, chat[0])
                            db_inthread.set_last_lessons_by_peer_id(chat[0], currentday)
                    time.sleep(4)
                time.sleep(51000)

        try:
            # Отправка текстового сообщения
            # asyncio.run(check_today_lessons_update())

            if oshibka==0:
                x = threading.Thread(target=check_today_lessons_update)
                x.start()

            for event in longpoll.listen():  # Постоянное прослушивание сообщений
                if event.type == VkBotEventType.MESSAGE_NEW:  # Проверка на приход сообщения
                    # Логика ответов
                    # Текстовые ответы -----------------------------------------------------------------------------
                    if db.chat_id_is_in_DB(event.obj.peer_id):
                        group_link = db.get_group_link_by_peer_id(event.obj.peer_id)
                        if event.obj.text == "/сегодня" or event.obj.text == "/с":
                            send_msg(parser.check_schedule_exist(days=0, group_link=group_link))
                        elif event.obj.text == "/завтра" or event.obj.text == "/з":
                            send_msg(parser.check_schedule_exist(days=1, group_link=group_link))
                        elif event.obj.text == "/послезавтра" or event.obj.text == "/пз":
                            send_msg(parser.check_schedule_exist(days=2, group_link=group_link))
                        elif event.obj.text == "/вчера" or event.obj.text == "/в":
                            send_msg(parser.check_schedule_exist(days=-1, group_link=group_link))
                        elif event.obj.text == "/позавчера" or event.obj.text == "/пв":
                            send_msg(parser.check_schedule_exist(days=-2, group_link=group_link))
                        elif "/дата" in event.obj.text or "/д" in event.obj.text:
                            chuncks = event.obj.text.split()
                            date = chuncks[1]
                            answer = parser.bydate(date=date, groupLink=group_link)
                            if answer.split("\n")[3] == "":
                                send_msg("Системе не удалось найти учебную неделю в расписании.")
                            else:
                                send_msg(answer)

                    else:
                        send_msg("Не выбранна группа для беседы. Воспользуйтесь командой /группа или /г")
                    if "/группа" in event.obj.text or "/г" in event.obj.text:
                        chuncks = event.obj.text.split()
                        group_name = chuncks[1].upper()
                        if db.group_name_is_in_DB(group_name):
                            db.review_ChatsT(peer_id=event.obj.peer_id, group_name=group_name)
                            send_msg("Ваш чат теперь привязан к группе " + group_name)
                        else:
                            send_msg("Неправельно введено название группы")
        except (requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError,
                urllib3.exceptions.NewConnectionError, socket.gaierror):
            oshibka = oshibka + 1
            print("Произошла ошибка" + '№' + str(oshibka) + " - ошибка подключения к вк!!! Бот будет перезапущен!!!")
            time.sleep(5.0)
            main()
        finally:
            oshibka = oshibka + 1
            print("Произошла ошибка" + '№' + str(oshibka) + "!!! Бот будет перезапущен!!!")
            main()
    except (requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError,
            urllib3.exceptions.NewConnectionError, socket.gaierror):
        oshibka = oshibka + 1
        print("Произошла ошибка" + '№' + str(oshibka) + " - ошибка подключения к вк!!! Бот будет перезапущен!!!")
        time.sleep(5.0)
        main()


if __name__ == '__main__':
    main()
    print("finish")
