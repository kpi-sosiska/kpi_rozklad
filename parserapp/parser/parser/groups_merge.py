from parserapp.parser.scrappers.campus.disciplines import get_disciplines


async def _merge_rozklad_with_campus(rozklad_groups, campus_groups):

    # если и в розкладе и в крампусе по 1 группе с одинаковым названием - считаем что это одна и та же группа
    if len(rozklad_groups) == len(campus_groups) == 1:
        yield merge_group(rozklad_groups[0], campus_groups[0])
        return

    # если не во всех группах указана кафедра, матчим по предметам
    if not all(rg._rozklad_cathedra() for rg in rozklad_groups):
        async for group in match_by_disciplines(rozklad_groups, campus_groups):
            yield group
    else:
        async for group in match_by_cathedras(rozklad_groups, campus_groups):
            yield group

    # оставшиеся группы отдаем без кампусовской инфы
    print('группы розклада без пары: ', rozklad_groups)
    for group in rozklad_groups:
        yield group

    # todo check


def merge_group(rozklad, campus):
    for i in ('id_campus', 'name', 'cathedra_id'):
        setattr(rozklad, i, getattr(campus, i))
    return rozklad


async def match_by_disciplines(rozklad_groups, campus_groups):
    for rg in rozklad_groups:

        if not campus_groups:  # закончились, т.е. len(campus_groups) < len(rozklad_groups)
            print("CAMPUS LESS GROUPS", rozklad_groups, campus_groups)
            return

        disciplines_r = {les.subject.name for les in rg._lessons}

        disciplines_c = {cg_: await get_disciplines(cg_.cathedra.name_campus)
                         for cg_ in campus_groups}

        # сортируем дисциплины кампуса по наибольшему количество совпадений с розкладом
        disciplines_c = sorted(disciplines_c.items(),
                               key=lambda cg_, dr=disciplines_r: len(dr.intersection(cg_[1])))

        cg = disciplines_c[0][0]  # выбираем группу по лучшему совпадению

        yield merge_group(rg, cg)
        campus_groups.remove(cg)


async def match_by_cathedras(rozklad_groups, campus_groups):
    for rg in rozklad_groups:
        cathedra_r = rg._rozklad_cathedra()

        for cs in campus_groups:
            if _check_cathedra_same(cathedra_r, cs.cathedra.name_short):
                yield merge_group(rg, cs)
                campus_groups.remove(cs)
                break
        else:
            # не нашло кампус к розкладу
            print("CAMPUS != ROZKLAD", rozklad_groups, campus_groups)
            # raise Exception(rg)


def _check_cathedra_same(roz, cam):
    cam_tryhard = cam.replace(' ', '').replace('та', 'і')
    return roz in (cam, cam_tryhard)

