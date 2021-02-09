import asyncio
import os

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kpi_rozklad.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

django.setup()

from parserapp.parser.campus import get_cathedras, get_faculties, find_group
from parserapp.parser.rozklad.group import get_group
from parserapp.parser.rozklad.groups import get_groups_list


async def try_(func, attempts=5):
    for attempt in range(attempts):
        try:
            return await func()
        except Exception as ex:
            print(type(ex), ex, attempt)
            if attempt == attempts-1:
                return ex


async def faculties_and_cathedras():
    faculties = await get_faculties()
    for faculty in faculties:
        faculty.save()
        cathedras = await get_cathedras(faculty)
        for c in cathedras:
            c.save()


async def groups():
    import aiohttp
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20))

    rozklad_groups_names = await get_groups_list(session)

    for group_name in rozklad_groups_names:
        rozklad_groups = await try_(lambda g=group_name: get_group(session, g))
        if isinstance(rozklad_groups, Exception):
            continue
        rozklad_groups = [g for g in rozklad_groups if g[1]]
        if not rozklad_groups:
            continue

        campus_groups = await try_(lambda g=group_name: find_group(g))
        campus_groups = [g for g in campus_groups if g.name == group_name]

        groups = merge_groups(rozklad_groups, campus_groups)

        if len(groups) != 1:
            for g, _ in groups:
                print(g.name_rozklad, end=' ')
            print(groups[0][0].name)
        else:
            print(groups[0][0].name, groups[0][0].url_rozklad)
        # for group, lessons in groups:
    await session.close()


async def main():
    await faculties_and_cathedras()
    # await groups()


def merge_groups(rozklad_groups, campus_groups):
    def merge_group(rozklad, campus):
        for i in ('id_campus', 'name', 'cathedra_id'):
            setattr(rozklad, i, getattr(campus, i))
        return rozklad

    if len(rozklad_groups) == len(campus_groups) == 1:
        yield merge_group(rozklad_groups[0], campus_groups[0])
        return

    for rg in rozklad_groups:
        cathedra = rg._group_info.rozklad_cathedra
        for cs in campus_groups:
            if cathedra in cs.cathedra.name:
                yield merge_group(rg, cs)
                break
        else:
            raise Exception(rg)

    # todo check


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
