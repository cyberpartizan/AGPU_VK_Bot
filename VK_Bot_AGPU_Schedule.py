from datetime import datetime
from datetime import timedelta
import socket
import threading
import time

import AGPU_Schedule_Parser as parser
import requests
import urllib3
import vk_api
from DataBase import Database
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# Импорт API ключа(токена)
# API_KEY = os.environ.get("API_KEY")
API_KEY = "6d3e7800807862b42f09c5b0adeb32c71d8646aef4e70ec1db414dba89d328d2e48e49486f2fdae46333d"
print("Бот работает...")
group_id = '197937466'  # Указываем id сообщества, изменять только здесь!
error = 0  # обнуление счетчика ошибок
threads = []
db = Database('AGPU_Schedule_Bot_DB.db')
Start_thread = True
q = True


def main():
    global error  # Счетчик ошибок
    try:
        vk_session = vk_api.VkApi(token=API_KEY)  # Авторизация под именем сообщества
        longpoll = VkBotLongPoll(vk_session, group_id)
        vk = vk_session.get_api()

        def send_msg(ms_g):
            vk.messages.send(peer_id=event.object.peer_id, random_id=0, message=ms_g)

        def send_msg_by_peer_id(ms_g, peer_id):
            vk.messages.send(peer_id=peer_id, random_id=0, message=ms_g)

        def check_today_lessons_update():  # Проверка на обновления расписания за день
            db_in_thread = Database('AGPU_Schedule_Bot_DB.db')
            while True:
                while ((datetime.now().hour >= 7) and (datetime.now().minute >= 30)) and (datetime.now().hour < 14):
                    chats = db_in_thread.get_send_updates_all()
                    for chat in chats:
                        currentday = chat[3]
                        if currentday != parser.today(group_link=chat[1]):
                            currentday = parser.today(group_link=chat[1])
                            send_msg_by_peer_id("Расписание изменилась \n \n" + currentday, chat[0])
                            db_in_thread.set_last_lessons_by_peer_id(chat[0], currentday)
                    time.sleep(1000)
                time_const= "7:30:00"
                FMT = "%H:%M:%S"
                delta_morning=datetime.strptime(time_const,FMT)- datetime.now()
                if delta_morning.days<0:
                    delta_morning = timedelta(days=0,seconds=delta_morning.seconds)
                time.sleep(int(delta_morning.total_seconds())+60)

        try:
            # Отправка текстового сообщения
            # asyncio.run(check_today_lessons_update())

            if error == 0:
                x = threading.Thread(target=check_today_lessons_update)
                x.start()

            for event in longpoll.listen():  # Постоянное прослушивание сообщений
                if event.type == VkBotEventType.MESSAGE_NEW:  # Проверка на приход сообщения
                    # Логика ответов
                    # Текстовые ответы -----------------------------------------------------------------------------
                    received_text = event.obj.text
                    peer_id = event.obj.peer_id
                    if db.chat_id_is_in_DB(peer_id):
                        group_link = db.get_group_link_by_peer_id(peer_id)
                        if received_text == "/сегодня" or received_text == "/с":
                            send_msg(parser.check_schedule_exist(days=0, group_link=group_link))
                        elif received_text == "/время":
                            send_msg(datetime.now())
                        elif received_text == "/завтра" or received_text == "/з":
                            send_msg(parser.check_schedule_exist(days=1, group_link=group_link))
                        elif received_text == "/послезавтра" or received_text == "/пз":
                            send_msg(parser.check_schedule_exist(days=2, group_link=group_link))
                        elif received_text == "/вчера" or received_text == "/в":
                            send_msg(parser.check_schedule_exist(days=-1, group_link=group_link))
                        elif received_text == "/позавчера" or received_text == "/пв":
                            send_msg(parser.check_schedule_exist(days=-2, group_link=group_link))
                        elif "/дата" in received_text or "/д" in received_text:
                            chunks = received_text.split()
                            date = chunks[1]
                            answer = parser.check_schedule_exist(date=date, group_link=group_link)
                            send_msg(answer)
                            # answer = parser.bydate(date=date, group_link=group_link)

                            # if "\n" not in answer:
                            #     send_msg(answer)
                            # elif answer.split("\n")[3] == "":
                            #     send_msg("Системе не удалось найти учебную неделю в расписании.")
                            # else:
                            #     send_msg(answer)
                        elif received_text == "/подписаться":
                            db.set_send_updates(peer_id=peer_id, status=True)
                            group_name = db.get_group_name_by_peer_id(peer_id)
                            send_msg("Вы подписались на автоматическую рассылку расписания группы:" + group_name)
                        elif received_text == "/отписаться":
                            db.set_send_updates(peer_id=peer_id, status=False)
                            group_name = db.get_group_name_by_peer_id(peer_id)
                            send_msg("Вы отписались от автоматической рассылки расписания группы:" + group_name)
                    else:
                        send_msg("Не выбранна группа для беседы. Воспользуйтесь командой /группа или /г "
                                 + "+ название группы заглавными буквами, например: "
                                 + "/г ВМ-ИВТ-3-1 или /группа ZММ-МАТИ-2-1")
                    if "/группа" in received_text or "/г" in received_text:
                        chunks = received_text.split()
                        group_name = chunks[1].upper()
                        if db.group_name_is_in_DB(group_name):
                            db.review_ChatsT(peer_id=peer_id, group_name=group_name)
                            db.set_send_updates(peer_id=peer_id, status=True)
                            send_msg("Ваш чат теперь привязан к группе "
                                     + group_name
                                     + ". Чтобы отписатся от рассылки используйте команду /отписка."
                                     + "Для повторной подписки, команду /подписка.")
                        else:
                            send_msg("Неправельно введено название группы")
        except (requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError,
                urllib3.exceptions.NewConnectionError, socket.gaierror):
            error = error + 1
            print("Произошла ошибка" + ' № ' + str(
                error) + " - ошибка подключения к вк!!! Бот будет перезапущен!!!(except 1)")
            time.sleep(5.0)
            main()
        # finally:
        #     error = error + 1
        #     print("Произошла ошибка" + ' № ' + str(error) + "!!! Бот будет перезапущен!!!(finally)")
        #     main()
    except (requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError,
            urllib3.exceptions.NewConnectionError, socket.gaierror):
        error = error + 1
        print(
            "Произошла ошибка" + '№' + str(error) + " - ошибка подключения к вк!!! Бот будет перезапущен!!!except 2")
        time.sleep(5.0)
        main()


if __name__ == '__main__':
    main()
    print("finish")
