from itertools import zip_longest

from bs4 import BeautifulSoup

from mainapp.models import Group, Lesson, Teacher, Room, Subject
from parserapp.parser.scrappers.rozklad.utils import RozkladRetryException, get_rozklad_uuid

GROUP_BY_NAME = {
    "__EVENTVALIDATION": "/wEdAAEAAAD/////AQAAAAAAAAAPAQAAAAUAAAAIsA3rWl3AM+6E94I5Tu9cRJoVjv0LAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHfLZVQO6kVoZVPGurJN4JJIAuaU",
    "ctl00$MainContent$ctl00$btnShowSchedule": "Розклад занять",
    '__EVENTTARGET': 'ctl00$MainContent$ddlSemesterType'
}
GROUP_BY_URL = {
    '__EVENTVALIDATION': '/wEdAAEAAAD/////AQAAAAAAAAAPAQAAAAYAAAAIsA3rWl3AM+6E94I5ke7WZqDu1maj7tZmCwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANqZqakPTbOP2+koNozn1gOvqUEW',
    '__EVENTTARGET': 'ctl00$MainContent$ddlSemesterType'
}

URL_SELECT_GROUP = "http://rozklad.kpi.ua/Schedules/ScheduleGroupSelection.aspx"

GROUPS_NOT_FOUND_STR = 'не знайдено!'


async def get_group_by_url(group_url, session):
    htmls = [await _group_html_by_url(group_url, semestr, session)
             for semestr in (1, 2)]
    return _make_group(group_url, htmls)


async def get_groups_by_name(group_name, session):
    group_url, html1 = await _group_html_by_name(group_name, session)

    if str(group_url) == URL_SELECT_GROUP:
        groups = await _parse_anomaly_groups(html1)
        return [_make_group(url_rozklad=group_url,
                            htmls=(
                                await _group_html_by_url(group_url, 1, session),
                                await _group_html_by_url(group_url, 2, session)
                            ),
                            name_rozklad=name_rozklad)
                for name_rozklad, group_url in groups]
    else:
        html2 = await _group_html_by_url(group_url, semestr=2, session=session)
        return [_make_group(group_url, (html1, html2), name_rozklad=group_name)]


#

def _make_group(url_rozklad, htmls, name_rozklad=None):
    uuid = get_rozklad_uuid(url_rozklad)
    group = Group(uuid_rozklad=uuid, name_rozklad=name_rozklad)
    group._lessons = list(_parse_lessons(htmls))
    return group


async def _parse_anomaly_groups(html):
    if GROUPS_NOT_FOUND_STR in html:
        return []
    links = BeautifulSoup(html, features='lxml').find('table').find_all('a')
    return [
        (link.text, 'http://rozklad.kpi.ua/Schedules/' + link.attrs['href'])
        for link in links
    ]


async def _group_html_by_name(group_name, session):
    async with session.post(URL_SELECT_GROUP,
                            data={"ctl00$MainContent$ctl00$txtboxGroup": group_name} | GROUP_BY_NAME) as resp:
        html = await resp.text()
        RozkladRetryException.check_html(html)
        return resp.url, html


async def _group_html_by_url(group_url, semestr, session):
    async with session.post(group_url, data={'ctl00$MainContent$ddlSemesterType': semestr} | GROUP_BY_URL) as resp:
        html = await resp.text()
        RozkladRetryException.check_html(html)
        return html


def _parse_lessons(semestrs_htmls):
    def parse_lesson(lesson):
        subjects, teachers, rooms, types = [], [], [], []

        for link in lesson.find_all('a'):
            href = link.attrs['href']

            if href.startswith('http://wiki'):
                subjects.append(Subject(name=link.text, url_name=href.removeprefix('http://wiki.kpi.ua/index.php/')))

            if href.startswith('/Schedules'):
                name, position = _parse_teacher_position(link.text)
                teachers.append(Teacher(name=name, position=position, uuid_rozklad=get_rozklad_uuid(href)))

            if href.startswith('http://maps'):
                room, _, type_ = link.text.partition(' ')
                lat, lon = href.split('=')[1].split(',')
                rooms.append(Room(name=room, lat=lat, lon=lon))
                types.append(type_)

        for su, te, ro, ty in zip_longest(subjects, teachers, rooms, types):
            yield Lesson(
                subject=su, teacher=te, room=ro, lesson_type=ty,
                semestr=semestr_i + 1, week=week_i + 1,
                day=day_i, num=lesson_i,
            )

    for semestr_i, semestr_html in enumerate(semestrs_htmls):
        week_tables = BeautifulSoup(semestr_html, features='lxml').find_all('table')

        for week_i, week_table in enumerate(week_tables):
            trs = week_table.find_all('tr')[1:]

            for lesson_i, tr in enumerate(trs):
                tds = tr.find_all('td')[1:]

                for day_i, td in enumerate(tds):
                    yield from parse_lesson(td)


POSITIONS = {
    'ас.': 'асистент',
    'доц.': 'доцент',
    'вик.': 'викладач',
    'ст.вик.': 'старший викладач',
    'проф.': 'професор',
    'зав.каф.': 'зав. кафедрою',
    'дек.': 'декан',
    # 'пос.': '',
}


def _parse_teacher_position(name):
    name = name.removeprefix('пос.')
    for pos_r, pos_norm in POSITIONS.items():
        if name.startswith(pos_r):
            return name.removeprefix(pos_r).strip(), pos_norm
    return name, None
