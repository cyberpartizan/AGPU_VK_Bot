import requests
from bs4 import BeautifulSoup
import datetime
import time
import threading
global URL
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
            lessons.append((hoursandwith[j]['hour'] + '\n' + daysandlessons[weekday]['lessons'][i]['lesson'] + '\n' +
                            daysandlessons[weekday]['lessons'][i + 1]['lesson']).replace('\n\n', '').replace(
                '\n(ВМ-ИВТ-2-1)', ''))
            i += 1
        else:
            if daysandlessons[weekday]['lessons'][i]['lesson'] != '':
                lessons.append(
                    (hoursandwith[j]['hour'] + '\n' + daysandlessons[weekday]['lessons'][i]['lesson']).replace('\n\n','').replace('\n(ВМ-ИВТ-2-1)', ''))
        i += 1
        j += 1
    return {'day': daysandlessons[weekday]['day'], 'dayLessons': lessons}


def get_week_lessons(hoursandwith, daysandlessons):  # Вычисление расписания за неделю
    week = []
    for i in range(1, 8):
        week.append(get_day_lessons(hoursandwith, daysandlessons, i))
    return week


def get_week_count_and_weekday(day, month, year):  # Вычисление недели в URL и номера дня недели
    startweek = 2357
    startday = datetime.date(2019, 9, 2)
    endday = datetime.date(year, month, day)
    plusweek = int((endday - startday).days / 7)
    weekday = endday.weekday() + 1
    weekcount = startweek + plusweek
    return {'weekday': weekday, 'weekcount': weekcount}


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
        else:
            print("Неправельный формат даты")
    return temp


def get_lesson_by_date(date):  # Расписание по дате
    hoursandwith = []
    daysandlessons = []
    datenumbers = split_date_to_numbers(date)
    weekCount_weekDay = get_week_count_and_weekday(datenumbers[0], datenumbers[1], datenumbers[2])
    finalURL = URL + str(weekCount_weekDay['weekcount'])
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
    return day


def today(days=0,groupLink=""):
    group = groupLink[0]
    global URL
    URL=f'https://it-institut.ru/Raspisanie/SearchedRaspisanie?OwnerId=118&SearchId={group}&WeekId='
    date = datetime.datetime.now().date() + datetime.timedelta(days=days)
    res = String_day(get_lesson_by_date(date))
    return res


def bydate(date,groupLink):
    group = groupLink[0]
    global URL
    URL = f'https://it-institut.ru/Raspisanie/SearchedRaspisanie?OwnerId=118&SearchId={group}&WeekId='
    day = get_lesson_by_date(date)
    res = String_day(day)
    return res


def check_today_schedule_change():  # Проверка если расписание изминилось на сегодня
    while True:
        currentday = today()
        while (datetime.datetime.now().hour >= 8) and (datetime.datetime.now().hour < 18):
            if currentday == today():
                time.sleep(900)
            else:
                currentday = today()
        time.sleep(51000)


def start_scan():
    thread = threading.Thread(target=check_today_schedule_change, daemon=True)
    thread.start()


def String_day(daydict):
    day = daydict['day'] + '\n\n'
    lessons = ''
    for lesson in daydict['dayLessons']:
        lessons = lessons + lesson + '\n\n'
    return day + lessons


def String_week(weekdict):
    WeekLessons = ''
    for daydict in weekdict:
        WeekLessons = WeekLessons + String_day(daydict) + '\n'
    return WeekLessons

# day20_4_2020=today(-100)
# print(String_day(day20_4_2020))
# start_scan()
# while True:
# time.sleep(5)
