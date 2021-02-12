import aiohttp

from mainapp.models import Teacher
from parserapp.parser.parser.utils import try_, async_bunch
from parserapp.parser.scrappers import get_teacher


async def teachers():
    async def _get_info(teacher):
        info = await try_(lambda t=teacher.url_rozklad: get_teacher(session, t))
        return teacher, info

    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20))

    tasks = [_get_info(teacher) for teacher in Teacher.objects.all()]
    for i, task in enumerate(async_bunch(tasks)):
        teacher, (full_name, teacher_cathedras) = await task
        teacher.full_name = full_name
        teacher.cathedras.add(*teacher_cathedras)
        teacher.save()
        print(i, len(tasks))

