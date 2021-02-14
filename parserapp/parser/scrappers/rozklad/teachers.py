import re

from bs4 import BeautifulSoup

from mainapp.models import Group
from parserapp.parser.scrappers.rozklad.utils import RozkladRetryException

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

    return full_name, cathedras_names, find_groups()
