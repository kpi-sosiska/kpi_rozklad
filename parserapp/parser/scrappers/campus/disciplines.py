import aiohttp

from parserapp.parser.scrappers.campus.utils import _req, cache_async

session = aiohttp.ClientSession()


@cache_async
async def get_disciplines(cathedra_name):
    disciplines = set()
    specialities = await _get_specialities(cathedra_name)
    for s in specialities:
        disciplines.update(await _get_disciplines(s))
    return disciplines


@cache_async
async def _get_specialities(cathedra_name):
    url = 'http://api.campus.kpi.ua/Directory/GetCathedra'
    res = await _req(url, name=cathedra_name, light=False)

    return [
        f['Name']
        for f in res['Data']['Specialities']
    ]


@cache_async
async def _get_disciplines(speciality_name):
    url = 'http://api.campus.kpi.ua/Directory/GetSpeciality'
    res = await _req(url, name=speciality_name, light=False)

    return [
        f['Title']
        for f in res['Data']['Disciplines']
        if f['Title']
    ]

