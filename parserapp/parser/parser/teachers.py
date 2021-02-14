from functools import reduce
from operator import or_

from django.db.models import Count, Q

from mainapp.models import Teacher, Cathedra, Faculty
from parserapp.parser.parser.utils import try_, async_bunch
from parserapp.parser.scrappers import get_teacher


async def update_all_teachers(session):
    tasks = [update_teacher(teacher, session) for teacher in Teacher.objects.all()]
    for i, task in enumerate(async_bunch(tasks)):
        await task
        print(i, len(tasks))


async def update_teacher(teacher_model, session):
    full_name, cathedras, groups = await try_(lambda t=teacher_model.url_rozklad: get_teacher(session, t))

    teacher_model.full_name = full_name
    teacher_model.cathedras.set(_get_cathedras(cathedras, groups), clear=True)

    teacher_model.save()


def _get_cathedras(cathedras_names, groups):
    def _cathedra_name_2_regex(cathedra_name):
        translation_dict = {
            ' №': '.*',
            'МАтаТІ': 'МАтаТЙ',
        }.items()
        cathedra_name = reduce(lambda a, i: a.replace(i[0], i[1]), translation_dict, cathedra_name)
        return '^' + cathedra_name

    def find_faculties():
        def find_faculties_():
            groups_ = list(groups)
            if not groups_:
                return []
            return Faculty.objects.filter(reduce(or_, [
                Q(cathedras__groups__name=g)
                for g in groups_
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

    return filter(None, [get_cathedra(cathedra_name) for cathedra_name in cathedras_names])
