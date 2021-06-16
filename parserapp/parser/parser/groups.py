from parserapp.parser.parser.utils import try_
from parserapp.parser.scrappers import get_disciplines, get_groups_by_name, get_group_by_url, get_groups_list, find_group


async def update_group_schedule(group_model, session):
    group = await try_(lambda g=group_model.url_rozklad: get_group_by_url(session, g))  # отсюда нужны только lessons
    group_model.save_with_lessons(group._lessons)


async def parse_and_save_all_groups(session):
    async for group in _parse_all_groups(session):
        group.save_with_lessons(group._lessons)


#


async def _parse_all_groups_names(session):
    # rozklad_groups_names = await get_groups_list(session)
    rozklad_groups_names = [s.strip() for s in open('parser/stuff/rozklad_groups_short.txt')]
    # rozklad_groups_names = rozklad_groups_names[rozklad_groups_names.index('ІК-01'):][:50]
    return rozklad_groups_names


async def _parse_all_groups(session):
    rozklad_groups_names = await _parse_all_groups_names(session)
    for group_name in rozklad_groups_names:
        groups = await _parse_groups_by_name(group_name, session)
        for g in groups:
            yield g


async def _parse_groups_by_name(group_name, session):
    rozklad_groups = await try_(lambda g=group_name: get_groups_by_name(g, session))

    rozklad_groups = [g for g in rozklad_groups if g._lessons]
    if not rozklad_groups:
        print("ROZKLAD NO GROUP ", group_name)
        return []

    campus_groups = await _find_campus_groups(group_name)
    if not campus_groups:
        print("CAMPUS NO GROUP ", group_name)
        return []

    return await _merge_rozklad_with_campus(rozklad_groups, campus_groups)


async def _merge_rozklad_with_campus(rozklad_groups, campus_groups):
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
                cathedra_c = cs.cathedra.name_short
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


async def _find_campus_groups(group_name):
    async def _find(name):
        campus_groups = await try_(lambda g=name: find_group(g))
        campus_groups = [g for g in campus_groups if g.name == name]
        return campus_groups

    # maybe group_name normalisation or smth
    return await _find(group_name)
