import re

from bs4 import BeautifulSoup

from mainapp.models import Group, Subject, Teacher, Room, Lesson
from parserapp.parser.scrappers.rozklad.group import GROUP_BY_URL, _parse_teacher_position
from parserapp.parser.scrappers.rozklad.utils import RozkladRetryException, get_rozklad_uuid

RE_NAME_CATHEDRA = re.compile(r'(.*) \((.*)\)')


async def get_teacher(session, url):
    async with session.post(url) as resp:
        html = await resp.text()

    def find_groups():
        for td in soup.find_all('td'):
            if td.find(class_='disLabel'):
                groups = list(td.children)[-1]
                groups = [i.group(0) for i in Group.RE_GROUP_CODE.finditer(groups)]
                yield from groups

    RozkladRetryException.check_html(html)
    soup = BeautifulSoup(html, features='lxml')
    header = soup.find(id='ctl00_MainContent_lblHeader')
    text = header.text.split('викладач: ')[1]

    full_name, cathedras_names = RE_NAME_CATHEDRA.search(text).groups()
    cathedras_names = cathedras_names.split(', ')
    cathedras_names = list(filter(None, cathedras_names))

    lessons = list(_parse_lessons([await _teacher_html_by_url(url, semestr, session)
               for semestr in (1, 2)]))

    return full_name, cathedras_names, find_groups(), lessons


def _parse_lessons(semestrs_htmls):
    def parse_lesson(lesson):
        subjects, teachers, rooms, types, groups = [], [], [], [], []

        for link in lesson.find_all('a'):
            href = link.attrs['href']

            if href.startswith('http://wiki'):
                subjects.append(Subject(name=link.text, url_name=href.removeprefix('http://wiki.kpi.ua/index.php/')))

            if href.startswith('/Schedules'):
                name, position = _parse_teacher_position(link.text)
                teachers.append(Teacher(name=name, position=position, uuid_rozklad=get_rozklad_uuid(href)))

                group_names = link.parent.contents[-1].split(", ")
                groups = [Group.find_by_name_rozklad(group_name) for group_name in group_names]

            if href.startswith('http://maps'):
                room, _, type_ = link.text.partition(' ')
                lat, lon = href.split('=')[1].split(',')
                rooms.append(Room(name=room, lat=lat, lon=lon))
                types.append(type_)

        for su, te, ro, ty, gr in zip(subjects, teachers, rooms, types, groups):
            yield Lesson(
                subject=su, teacher=te, room=ro, lesson_type=ty,
                semestr=semestr_i + 1, week=week_i + 1,
                day=day_i, num=lesson_i, group=gr
            )

    for semestr_i, semestr_html in enumerate(semestrs_htmls):
        week_tables = BeautifulSoup(semestr_html, features='lxml').find_all('table')

        for week_i, week_table in enumerate(week_tables):
            trs = week_table.find_all('tr')[1:]

            for lesson_i, tr in enumerate(trs):
                tds = tr.find_all('td')[1:]

                for day_i, td in enumerate(tds):
                    yield from parse_lesson(td)


async def _teacher_html_by_url(teacher_url, semestr, session):
    async with session.post(teacher_url, data={'ctl00$MainContent$ddlSemesterType': semestr} | GROUP_BY_URL) as resp:
        html = await resp.text()
        RozkladRetryException.check_html(html)
        return html
