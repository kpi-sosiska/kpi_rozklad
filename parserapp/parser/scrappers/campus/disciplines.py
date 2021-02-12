import functools

import aiohttp

session = aiohttp.ClientSession()


def cache_async(func):
    cache = dict()

    @functools.wraps(func)
    async def wrapper(*args):
        if args not in cache:
            cache[args] = await func(*args)
        return cache[args]

    return wrapper


async def _req(url, **data):
    async with session.get(url, data=data) as resp:
        return await resp.json()


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

