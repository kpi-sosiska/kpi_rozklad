import asyncio

from django.db import transaction

from parserapp.parser import get_faculties, get_cathedras, get_groups_list, get_group, get_disciplines, find_group


async def main():
    await faculties_and_cathedras()
    await groups()


async def faculties_and_cathedras():
    faculties = await get_faculties()
    for faculty in faculties:
        with transaction.atomic():
            faculty.save()
            cathedras = await get_cathedras(faculty)
            for c in cathedras:
                c.save()


async def groups():
    async for group in get_groups():
        with transaction.atomic():
            group.save()
            group.lesson_set.all().delete()
            for lesson in group._lessons:
                lesson.teacher.save()
                lesson.room.save()
                lesson.subject.save()
                lesson.group = group
                lesson.save()


async def get_groups():
    import aiohttp
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20))

    # rozklad_groups_names = await get_groups_list(session)
    rozklad_groups_names = [s.strip() for s in open('parser/rozklad_groups_short.txt')]
    rozklad_groups_names = rozklad_groups_names[rozklad_groups_names.index('ІК-01'):][:50]

    for group_name in rozklad_groups_names:
        rozklad_groups = await try_(lambda g=group_name: get_group(session, g))

        rozklad_groups = [g for g in rozklad_groups if g._lessons]
        if not rozklad_groups:
            continue

        campus_groups = await find_campus_groups(group_name)
        if not campus_groups:
            print("CAMPUS NO GROUP ", group_name)
            continue

        groups = await merge_rozklad_with_campus(rozklad_groups, campus_groups)
        for g in groups:
            yield g
    await session.close()



async def merge_rozklad_with_campus(rozklad_groups, campus_groups):
    def merge_group(rozklad, campus):
        for i in ('id_campus', 'name', 'cathedra_id'):
            setattr(rozklad, i, getattr(campus, i))
        return rozklad

    async def match_by_disciplines():
        for rg in rozklad_groups:
            disciplines_r = {les.subject.name for les in rg._lessons}
            cgs = [(cg_, await get_disciplines(cg_.cathedra.name_campus)) for cg_ in campus_groups]
            cgs = sorted(cgs, key=lambda cg_, dr=disciplines_r: len(dr.intersection(cg_[1])))
            if not cgs:
                print("CAMPUS LESS GROUPS", rozklad_groups, campus_groups)
                return
            cg = cgs[0][0]

            yield merge_group(rg, cg)
            campus_groups.remove(cg)

    async def match_by_cathedras():
        for rg in rozklad_groups:
            cathedra_r = rg._rozklad_cathedra()
            for cs in campus_groups:
                cathedra_c = cs.cathedra.name.rsplit(' ', 1)[0]
                if cathedra_r in cathedra_c or cathedra_r in cathedra_c.replace(' ', '').replace('та', 'і'):
                    yield merge_group(rg, cs)
                    campus_groups.remove(cs)
                    break
            else:
                print("CAMPUS != ROZKLAD", rozklad_groups, campus_groups)
                # не нашло кампус к розкладу
                # raise Exception(rg)

    if len(rozklad_groups) == len(campus_groups) == 1:
        return [merge_group(rozklad_groups[0], campus_groups[0])]

    if not all(rg._rozklad_cathedra() for rg in rozklad_groups):
        # не во всех группах указана кафедра
        return [g async for g in match_by_disciplines()]

    return [g async for g in match_by_cathedras()]

    # todo check


async def find_campus_groups(group_name):
    async def _find(name):
        campus_groups = await try_(lambda g=name: find_group(g))
        campus_groups = [g for g in campus_groups if g.name == name]
        return campus_groups

    # _ = Group._parse_name(group_name)
    # normalized_group_name = ''.join((
    #     _.prefix, '-', _.m1.replace('п', ''),
    #     _.year, _.number,
    #     _.m2 + ('п' if 'п' in _.m1 else '')
    # ))
    # print(normalized_group_name)

    g = await _find(group_name)
    return g


async def try_(func, attempts=5):
    for attempt in range(attempts - 1):
        try:
            return await func()
        except Exception as ex:
            print(type(ex), ex, attempt)
    return await func()




if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
