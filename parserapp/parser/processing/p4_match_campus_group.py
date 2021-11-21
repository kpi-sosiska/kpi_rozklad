import itertools
from collections import defaultdict

from mainapp.models import Group
from parserapp.parser.processing.utils import try_
from parserapp.parser.scrappers import find_group
from parserapp.parser.scrappers.campus.disciplines import get_disciplines



def reset_campus():
    print("reset_campus")
    Group.objects.all().update(name=None, id_campus=None, cathedra_id=None)


async def match_campus_to_all_groups(session, skip_matched=False):
    print("match_campus_to_all_groups")

    all_groups = Group.objects.all()
    groups_by_name = defaultdict(list)
    for group in all_groups:
        groups_by_name[group.name_rozklad_normalized].append(group)

    for i, (group_name, rozklad_groups) in enumerate(groups_by_name.items()):
        campus_groups = await _find_campus_groups(group_name)
        async for g in _merge_rozklad_with_campus(rozklad_groups, campus_groups):
            g.save()
        print(i, len(groups_by_name))


async def _find_campus_groups(group_name):
    async def _find(name):
        campus_groups = await try_(lambda g=name: find_group(g))
        campus_groups = [g for g in campus_groups if g.name == name]
        return campus_groups

    # maybe group_name normalisation or smth
    return await _find(group_name)


async def _merge_rozklad_with_campus(rozklad_groups, campus_groups):
    # если и в розкладе и в крампусе по 1 группе с одинаковым названием - считаем что это одна и та же группа
    if len(rozklad_groups) == len(campus_groups) == 1:
        yield _merge_group(rozklad_groups[0], campus_groups[0])
        return

    # матчинг по предметам и кафедрам
    async for group in _match(rozklad_groups, campus_groups):
        yield group

    if rozklad_groups:
        # оставшиеся группы отдаем без кампусовской инфы
        print('группы розклада без пары: ', rozklad_groups[0].name_rozklad, rozklad_groups)
        for group in rozklad_groups:
            yield group

    # todo check


async def _match(rozklad_groups, campus_groups):
    for g in rozklad_groups:
        g.disciplines = {_normalize_subject_name(les.subject.name_normalized) for les in g.lessons.all()}

    for g in campus_groups:
        g.disciplines = {_normalize_subject_name(n) for n in await get_disciplines(g.cathedra.name_campus)}

    overlaps = {
        (rg, cg): _matching_points(rg, cg)
        for rg, cg in itertools.product(rozklad_groups, campus_groups)
    }
    overlaps = sorted(overlaps.items(), key=lambda i: -i[1])

    for (rg, cg), _ in overlaps:
        if rg in rozklad_groups and cg in campus_groups:
            yield _merge_group(rg, cg)
            rozklad_groups.remove(rg)
            campus_groups.remove(cg)


def _merge_group(rozklad, campus):
    for i in ('id_campus', 'name', 'cathedra_id'):
        setattr(rozklad, i, getattr(campus, i))
    return rozklad


def _matching_points(rg, cg):
    def _check_cathedra_same(roz, cam):
        cam_tryhard = cam.replace(' ', '').replace('та', 'і')
        return roz in (cam, cam_tryhard)

    subject_intersections = len(rg.disciplines.intersection(cg.disciplines))
    same_cathedra = _check_cathedra_same(rg._rozklad_cathedra(), cg.cathedra.name_short)

    return subject_intersections + int(same_cathedra) * 50


def _normalize_subject_name(name):
    return name.lower().replace(' ', '')
