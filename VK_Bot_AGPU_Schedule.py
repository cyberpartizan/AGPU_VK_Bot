import socket
import requests
import urllib3
import vk_api
import datetime
import AGPU_Schedule_Parser as parser
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import time
import DataBase as db

# Импорт API ключа(токена) из отдельного файла
APIKEYSS = "6d3e7800807862b42f09c5b0adeb32c71d8646aef4e70ec1db414dba89d328d2e48e49486f2fdae46333d"
print("Бот работает...")
group_id = '197937466'  # Указываем id сообщества, изменять только здесь!
oshibka = 0  # обнуление счетчика ошибок


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

            def check_schedule_existans(group_link,days=0):#Проверяет существоавания расписания
                schedule_text = parser.today(days=days,groupLink=group_link)
                if schedule_text.split("\n")[3] == "":
                    return "Системе не удалось найти учебную неделю в расписании."
                else:
                    return schedule_text

            for event in longpoll.listen():  # Постоянное прослушивание сообщений
                if event.type == VkBotEventType.MESSAGE_NEW:  # Проверка на приход сообщения
                    # Логика ответов
                    # Текстовые ответы -----------------------------------------------------------------------------
                    if db.chat_id_is_in_DB(event.obj.peer_id):
                        group_link = db.get_group_link_by_peer_id(event.obj.peer_id)
                        if event.obj.text == "/сегодня" or event.obj.text == "/с":
                            send_msg(check_schedule_existans(days=0, group_link=group_link))
                        elif event.obj.text == "/завтра" or event.obj.text == "/з":
                            send_msg(check_schedule_existans(days=1, group_link=group_link))
                        elif event.obj.text == "/послезавтра" or event.obj.text == "/пз":
                            send_msg(check_schedule_existans(days=2, group_link=group_link))
                        elif event.obj.text == "/вчера" or event.obj.text == "/в":
                            send_msg(check_schedule_existans(days=-1, group_link=group_link))
                        elif event.obj.text == "/позавчера" or event.obj.text == "/пв":
                            send_msg(check_schedule_existans(days=-2, group_link=group_link))
                        elif "/дата" in event.obj.text or "/д" in event.obj.text:
                            chuncks = event.obj.text.split()
                            date = chuncks[1]
                            answer = parser.bydate(date=date, groupLink=group_link)
                            if answer.split("\n")[3]=="":
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

