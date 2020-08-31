import datetime

import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}


def get_html(url, headers, params=None):  # HTML страница
    r = requests.get(url, headers=headers, params=params)
    return r.text


def get_content(html):  # Конвертация в BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_day_lessons(hoursandwith, daysandlessons, weekday):  # Вычисления расписания за день
    weekday = weekday - 1
    i = 0
    j = 0
    lessons = []
    while j <= len(hoursandwith) - 1:  # Вычисление пустых клеток и обнаружение двух клеток в одной
        if (hoursandwith[j]['hourWidth'] == '2') and (daysandlessons[weekday]['lessons'][i]['lessonWidth'] == '1'):
            lessons.append(
                (hoursandwith[j]['hour']
                 + '\n'
                 + daysandlessons[weekday]['lessons'][i]['lesson']
                 + '\n' + daysandlessons[weekday]['lessons'][i + 1]['lesson'])
                    .replace('\n\n', '')
            )
            i += 1
        else:
            if daysandlessons[weekday]['lessons'][i]['lesson'] != '':
                lessons.append(
                    (hoursandwith[j]['hour']
                     + '\n'
                     + daysandlessons[weekday]['lessons'][i]['lesson'])
                        .replace('\n\n', '')
                )
        i += 1
        j += 1
    return {'day': daysandlessons[weekday]['day'], 'dayLessons': lessons}


def get_week_lessons(hoursandwith, daysandlessons):  # Вычисление расписания за неделю
    week = []
    for i in range(1, 8):
        week.append(get_day_lessons(hoursandwith, daysandlessons, i))
    return week


def get_week_count_and_weekday(datenumbers):  # Вычисление недели в URL и номера дня недели
    startweek = 2613
    try:
        day = datenumbers[0]
        month = datenumbers[1]
        year = datenumbers[2]
    except ValueError:
        print("Не правельный формат даты")
    startday = datetime.date(2020, 8, 31)
    endday = datetime.date(year, month, day)
    plusweek = int((endday - startday).days / 7)
    weekday = endday.weekday() + 1
    weekcount = startweek + plusweek
    return {'weekday': weekday, 'weekcount': weekcount}


def check_date_format(date_string):
    try:
        if "." in date_string:
            date_format = "%d.%m.%Y"
        elif "," in date_string:
            date_format = "%d,%m,%Y"
        elif "-" in date_string:
            date_format = "%d-%m-%Y"
        elif "/" in date_string:
            date_format = "%d/%m/%Y"
        else:
            return False
        datetime.datetime.strptime(date_string, date_format)
    except ValueError:
        return False
    else:
        return True


def split_date_to_numbers(date):  # Разделение даты по дням / месяцам / лет
    temp = []
    if type(date) == datetime.date:
        temp.append(date.day)
        temp.append(date.month)
        temp.append(date.year)
    else:
        if "." in date:
            temp = list(map(int, date.split('.')))
        elif "," in date:
            temp = list(map(int, date.split(',')))
        elif "/" in date:
            temp = list(map(int, date.split('/')))
        elif "-" in date:
            temp = list(map(int, date.split('-')))
        else:
            return print("Неправельный формат даты")
    return temp


def get_lesson_by_date(date, grouplink):  # Расписание по дате
    hoursandwith = []
    daysandlessons = []
    if type(date) == datetime.date or check_date_format(date):
        datenumbers = split_date_to_numbers(date)
        weekCount_weekDay = get_week_count_and_weekday(datenumbers)
        WeekNumber = str(weekCount_weekDay['weekcount'])
        finalURL = f'https://it-institut.ru/Raspisanie/SearchedRaspisanie?OwnerId=118&SearchId={grouplink}&WeekId={WeekNumber}'
        html = get_html(finalURL, headers)
        content = get_content(html)
        tr = content.findAll('tr')  # Находим все строки таблицы (включая заголовки)
        for th in tr[0].findAll('th')[1:]:  # Заголовки и их ширина
            hoursandwith.append({'hour': th.find('span').get_text(),
                                 'hourWidth': th['colspan']
                                 })

        for line in tr[1:]:  # Пары и их ширина
            temp = []
            for lesson in line.findAll('td'):
                temp.append({'lesson': lesson.get_text(separator='\n'),
                             'lessonWidth': lesson['colspan']})
            daysandlessons.append({'day': line.find('th').get_text(separator='\n'),
                                   'lessons': temp})

        day = (get_day_lessons(hoursandwith, daysandlessons, weekCount_weekDay['weekday']))
    else:
        return "Ошибка при указании даты"
    return day


def today(group_link, days=0):
    global URL
    URL = f'https://it-institut.ru/Raspisanie/SearchedRaspisanie?OwnerId=118&SearchId={group_link}&WeekId='
    date = datetime.datetime.now().date() + datetime.timedelta(days=days)
    res = String_day(get_lesson_by_date(date=date, grouplink=group_link))
    return res


def bydate(date, group_link):
    global URL
    day = get_lesson_by_date(date=date, grouplink=group_link)
    res = String_day(day)
    return res


# def check_today_schedule_change(group_link):  # Проверка если расписание изминилось на сегодня
#    while True:
#        currentday = today(groupLink=group_link)
#        while (datetime.datetime.now().hour >= 8) and (datetime.datetime.now().hour < 18):
#            if currentday == today():
#                time.sleep(900)
#            else:
#                currentday = today()
#        time.sleep(51000)

# async def check_today_schedule_change(peer_id, group_link):  # Проверка если расписание изминилось на сегодня
#    #currentday = today(groupLink=group_link)
#    while (get_send_updates_status_one(peer_id) and datetime.datetime.now().hour >= 8) and (datetime.datetime.now().hour < 18):
#        if currentday == today(groupLink=group_link):
#            await asyncio.time.sleep(900)
#        else:
#            currentday = today(groupLink=group_link)
#            send_msg_by_peer_id(currentday, peer_id)
#    await asyncio.time.sleep(51000)

def String_day(daydict):
    if type(daydict) is dict:
        day = daydict['day'] + '\n\n'
        lessons = ''
        for lesson in daydict['dayLessons']:
            lessons = lessons + lesson + '\n\n'
        return day + lessons
    else:
        return daydict


def String_week(weekdict):
    WeekLessons = ''
    for daydict in weekdict:
        WeekLessons = WeekLessons + String_day(daydict) + '\n'
    return WeekLessons


def check_schedule_exist(group_link, date=None, days=0):  # Проверяет существоавания расписания
    if date != None:
        schedule_text = bydate(date=date, group_link=group_link)
        if "\n" not in schedule_text:
            return schedule_text
    else:
        schedule_text = today(days=days, group_link=group_link)
    if schedule_text.split("\n")[3] == "":
        return "Системе не удалось найти учебную неделю в расписании."
    else:
        return schedule_text

# day20_4_2020=today(-100)
# print(String_day(day20_4_2020))
# start_scan()
# while True:
# time.sleep(5)
# print(check_date_format("9;3/2020"))
