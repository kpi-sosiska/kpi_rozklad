import re
from functools import reduce
from operator import or_

from bs4 import BeautifulSoup
from django.db.models import Q, Count

from mainapp.models import Cathedra, Faculty, Group
from parserapp.parser.scrappers.rozklad.utils import RozkladRetryException

RE_NAME_CATHEDRA = re.compile(r'(.*) \((.*)\)')


async def get_teacher(session, url):
    async with session.post(url) as resp:
        html = await resp.text()

    def _cathedra_name_2_regex(cathedra_name):
        translation_dict = {
            ' №': '.*',
            'МАтаТІ': 'МАтаТЙ',
        }.items()
        cathedra_name = reduce(lambda a, i: a.replace(i[0], i[1]), translation_dict, cathedra_name)
        return '^' + cathedra_name

    def find_faculties():
        def find_groups():
            for td in soup.find_all('td'):
                if td.find(class_='disLabel'):
                    groups = list(td.children)[-1]
                    groups = [i.group(0) for i in Group.RE_GROUP_CODE.finditer(groups)]
                    yield from groups

        def find_faculties_():
            groups = list(find_groups())
            if not groups:
                return []
            return Faculty.objects.filter(reduce(or_, [
                Q(cathedras__groups__name=g)
                for g in groups
            ])).annotate(cnt=Count('id_campus')).order_by('-cnt').values_list('id_campus', flat=True)

        if not getattr(find_faculties, 'res', None):
            find_faculties.res = find_faculties_()
        return find_faculties.res

    def get_cathedra(cathedra_name):
        cathedras_ = Cathedra.objects.filter(name_short__iregex=_cathedra_name_2_regex(cathedra_name))
        if cathedras_.count() == 0:
            return None
        if cathedras_.count() == 1:
            return cathedras_[0]
        faculties = find_faculties()
        if not faculties:
            return None
        cathedras_ = cathedras_.filter(faculty__id_campus__in=find_faculties())
        if cathedras_.count() == 0:
            return None
        return cathedras_[0]

    RozkladRetryException.check_html(html)

    soup = BeautifulSoup(html, features='lxml')
    header = soup.find(id='ctl00_MainContent_lblHeader')
    text = header.text.split('викладач: ')[1]

    full_name, cathedras_names = RE_NAME_CATHEDRA.search(text).groups()
    cathedras = [get_cathedra(cathedra_name) for cathedra_name in cathedras_names.split(', ')]
    cathedras = filter(None, cathedras)

    return full_name, cathedras
