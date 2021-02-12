from django.db import transaction

from parserapp.parser.scrappers import get_faculties, get_cathedras


async def faculties_and_cathedras():
    faculties = await get_faculties()
    for faculty in faculties:
        with transaction.atomic():
            faculty.save()
            cathedras = await get_cathedras(faculty)
            for c in cathedras:
                c.name_short = c.name if ' при ' in c.name else \
                               c.name.removesuffix(faculty.name).strip()
                c.save()
