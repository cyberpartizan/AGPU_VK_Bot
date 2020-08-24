import socket
import sqlite3
import requests
import urllib3
import vk_api
import AGPU_Schedule_Parser as parser
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import time


# Импорт API ключа(токена) из отдельного файла
APIKEYSS = "6d3e7800807862b42f09c5b0adeb32c71d8646aef4e70ec1db414dba89d328d2e48e49486f2fdae46333d"
print("Бот работает...")
group_id = '197937466'  # Указываем id сообщества, изменять только здесь!
oshibka = 0  # обнуление счетчика ошибок

connection = sqlite3.connect('Group.db')
cursor = connection.cursor()

def get_Link_from_db(Name):
    cursor.execute("SELECT groupLink FROM Groups WHERE groupName=:NameKey",{'NameKey':Name})
    return cursor.fetchone()

def main():
    global oshibka  # Счетчик ошибок
    try:
        vk_session = vk_api.VkApi(token=APIKEYSS)  # Авторизация под именем сообщества
        longpoll = VkBotLongPoll(vk_session, group_id)
        vk = vk_session.get_api()
        try:
            # Отправка текстового сообщения

            def send_msg(ms_g):
                vk.messages.send(peer_id=event.object.peer_id, random_id=0, message=ms_g)

            for event in longpoll.listen():  # Постоянный листинг сообщений
                if event.type == VkBotEventType.MESSAGE_NEW:  # Проверка на приход сообщения
                    # Логика ответов
                    # Текстовые ответы -----------------------------------------------------------------------------
                    group_Link=get_Link_from_db("ВМ-Мат-3-1")
                    if event.obj.text == "/сегодня" or event.obj.text == "/с":
                        send_msg(parser.today(groupLink=group_Link))
                    elif event.obj.text == "/завтра" or event.obj.text == "/з":
                        send_msg(parser.today(1,groupLink=group_Link))
                    elif event.obj.text == "/послезавтра" or event.obj.text == "/пз":
                        send_msg(parser.today(2,groupLink=group_Link))
                    elif event.obj.text == "/вчера" or event.obj.text == "/в":
                        send_msg(parser.today(-1,groupLink=group_Link))
                    elif event.obj.text == "/позавчера" or event.obj.text == "/пв":
                        send_msg(parser.today(-2,groupLink=group_Link))
                    elif "/дата" in event.obj.text or "/д" in event.obj.text:
                        split = event.obj.text.split()
                        date = split[1]
                        answer=parser.bydate(date,groupLink=group_Link)
                        send_msg(answer)


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
