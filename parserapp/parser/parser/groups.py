import aiohttp

from mainapp.models import Group
from parserapp.parser.parser.groups_merge import _merge_rozklad_with_campus
from parserapp.parser.parser.utils import try_
from parserapp.parser.scrappers import get_groups_by_name, get_group_by_url, get_groups_list, find_group
from parserapp.parser.scrappers.rozklad.utils import RozkladRetryException


async def update_group_schedule(group_model, session):
    group = await try_(lambda g=group_model.url_rozklad: get_group_by_url(session, g))  # отсюда нужны только lessons
    group_model.save_with_lessons(group._lessons)


async def parse_and_save_all_groups(session, skip_saved=False, skip_empty=False):
    async for group in _parse_all_groups(session, skip_saved, skip_empty):
        group.save_with_lessons(group._lessons)


#

async def _parse_all_groups(session, skip_saved=False, skip_empty=False):
    rozklad_groups_names = await _parse_all_groups_names(session, skip_saved, skip_empty)

    for i, group_name in enumerate(rozklad_groups_names):
        groups = await _parse_groups_by_name(group_name, session)
        print(i, len(rozklad_groups_names))
        if groups is not None:
            async for g in groups:
                yield g


async def _parse_all_groups_names(session, skip_saved=False, skip_empty=False):
    rozklad_groups_names = await get_groups_list(session)
    # rozklad_groups_names = [s.strip() for s in open('parser/stuff/rozklad_groups_short.txt')]

    rozklad_groups_names = set(rozklad_groups_names)

    if skip_saved:
        rozklad_groups_names -= set(Group.objects.all().values_list('name_rozklad', flat=True))

    if skip_empty:
        rozklad_groups_names -= {s.strip() for s in open('parser/stuff/rozklad_empty.txt')}

    return list(sorted(rozklad_groups_names))



async def _parse_groups_by_name(group_name, session):
    try:
        rozklad_groups = await try_(lambda g=group_name: get_groups_by_name(g, session), attempts=5)
    except (RozkladRetryException, aiohttp.client.ClientError):
        return

    rozklad_groups = [g for g in rozklad_groups if g._lessons]
    if not rozklad_groups:
        open('parser/stuff/rozklad_empty.txt', 'a').write(group_name + '\n')
        print("ROZKLAD NO GROUP ", group_name)
        return

    campus_groups = await _find_campus_groups(group_name)
    return _merge_rozklad_with_campus(rozklad_groups, campus_groups)


async def _find_campus_groups(group_name):
    async def _find(name):
        campus_groups = await try_(lambda g=name: find_group(g))
        campus_groups = [g for g in campus_groups if g.name == name]
        return campus_groups

    # maybe group_name normalisation or smth
    return await _find(group_name)
