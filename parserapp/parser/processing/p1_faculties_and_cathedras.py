from django.db import transaction

from parserapp.parser.scrappers import get_faculties, get_cathedras


async def save_faculties_and_cathedras():
    print("save_faculties_and_cathedras")


    faculties = await get_faculties()
    for faculty in faculties:
        with transaction.atomic():
            faculty.save()
            cathedras = await get_cathedras(faculty)
            for c in cathedras:
                c.name_short = get_short_name(c, faculty)
                c.save()


def get_short_name(cath, fac):
    if ' при ' in cath.name:
        return cath.name.split(' при ')[0]

    name = cath.name.removesuffix(fac.name)
    name = name.removesuffix(' ІПСА')
    return name.strip()
