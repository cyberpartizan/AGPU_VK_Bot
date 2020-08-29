import asyncio
import threading
import time
import datetime
import DataBase as db


async def main(loop):
    tasks = []
    for i in range(3):
        task = asyncio.create_task(func(i))
        tasks.append(task)
    await asyncio.gather(*tasks)


async def func():
    while (datetime.datetime.now().hour >= 8) and (datetime.datetime.now().hour < 18):
        chats = db.get_send_updates()
        for chat in chats:
            currentday = chat[3]
            if currentday != today(groupLink=chat[1]):
                currentday = today(groupLink=chat[1])
                send_msg_by_peer_id("Расписание изменилась \n \n" + currentday, chat[0])
                db.set_last_lessons_by_peer_id(chat[0])
        await asyncio.time.sleep(1000)
    await asyncio.time.sleep(51000)


async def check_today_schedule_change(peer_id, group_link):  # Проверка если расписание изминилось на сегодня
    chats = db.get_send_updates()
    while get_send_updates_status_one(peer_id):
        currentday = today(groupLink=group_link)
        while (datetime.datetime.now().hour >= 8) and (datetime.datetime.now().hour < 18):
            if currentday == today(groupLink=group_link):
                await asyncio.time.sleep(900)
            else:
                currentday = today(groupLink=group_link)
                send_msg_by_peer_id(currentday, peer_id)
        await asyncio.time.sleep(51000)

async def func2():
    print("func 2")
    await asyncio.sleep(2)

async def func3():
    print("func 3")
    await asyncio.sleep(1)

async def main2():
    tasks = []
    for i in range(5):
        task = asyncio.create_task(func2())
        await asyncio.gather(task)
        if i ==1:
            task = asyncio.create_task(func3())
            await asyncio.gather(task)


if __name__ == '__main__':
    print(datetime.datetime.now())



