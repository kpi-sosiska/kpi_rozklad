from bs4 import BeautifulSoup

from mainapp.models import Group, Lesson, Teacher, Room, Subject

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


async def get_group(session, group_name):
    def make_group(group_name_, group_url, html1, html2):
        group = Group(name=group_name, name_rozklad=group_name_, url_rozklad=group_url)
        lessons = parse_lessons((html1, html2), group=group)
        group._lessons = list(lessons)
        return group

    def parse_lessons(semestrs, group):
        def parse_lesson(lesson):
            subjects, teachers, rooms, types = [], [], [], []
            for link in lesson.find_all('a'):
                href = link.attrs['href']
                if href.startswith('http://wiki'):
                    subjects.append(Subject(name=link.text, url_wiki=href))
                if href.startswith('/Schedules'):
                    teachers.append(Teacher(name=link.text, url_rozklad='http://rozklad.kpi.ua' + href))
                if href.startswith('http://maps'):
                    room, _, type_ = link.text.rpartition(' ')
                    lat, lon = href.split('=')[1].split(',')
                    rooms.append(Room(name=room, lat=lat, lon=lon))
                    types.append(type_)
            for su, te, ro, ty in zip(subjects, teachers, rooms, types):
                yield Lesson(
                    subject=su, teacher=te, room=ro,
                    lesson_type=ty, group=group,
                    lesson_semestr=semestr_i+1, lesson_week=week_i+1,
                    lesson_day=day_i, lesson_num=lesson_i,
                )

        for semestr_i, semestr_html in enumerate(semestrs):
            week_tables = BeautifulSoup(semestr_html, features='lxml').find_all('table')

            for week_i, week_table in enumerate(week_tables):
                trs = week_table.find_all('tr')[1:]

                for lesson_i, tr in enumerate(trs):
                    tds = tr.find_all('td')[1:]

                    for day_i, td in enumerate(tds):
                        yield from parse_lesson(td)

    async def parse_anomaly_groups(html):
        if GROUPS_NOT_FOUND_STR in html:
            return []
        soup = BeautifulSoup(html, features='lxml')
        links = soup.find('table').find_all('a')
        return [
            (link.text, 'http://rozklad.kpi.ua/Schedules/' + link.attrs['href'])
            for link in links
        ]

    async def group_by_name(group_name):
        async with session.post(URL_SELECT_GROUP, data={"ctl00$MainContent$ctl00$txtboxGroup": group_name} | GROUP_BY_NAME) as resp:
            return resp.url, await resp.text()

    async def group_by_url(group_url, semestr):
        async with session.post(group_url, data={'ctl00$MainContent$ddlSemesterType': semestr} | GROUP_BY_URL) as resp:
            return await resp.text()

    group_url, html1 = await group_by_name(group_name)
    if str(group_url) == URL_SELECT_GROUP:
        groups = await parse_anomaly_groups(html1)
        return [
            make_group(
                group_name_, group_url,
                await group_by_url(group_url, semestr=1),
                await group_by_url(group_url, semestr=2)
            )
            for group_name_, group_url in groups
        ]
    else:
        html2 = await group_by_url(group_url, semestr=2)
        return [make_group(group_name, group_url, html1, html2)]
