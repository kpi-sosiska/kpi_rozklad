import aiohttp

from mainapp.models import Faculty, Cathedra, Group

session = aiohttp.ClientSession()


async def _req(url, **data):
    async with session.get(url, data=data) as resp:
        return await resp.json()


async def get_faculties():
    url = 'http://api.campus.kpi.ua/Directory/GetFaculties'
    res = await _req(url)
    return [
        Faculty(
            id_campus=f['Id'],
            name=f['ShortTitle'],
            name_campus=f['Name'],
            title=f['Title']
        )
        for f in res['Data']
    ]


async def get_cathedras(faculty):
    url = 'http://api.campus.kpi.ua/Directory/GetFaculty'
    res = await _req(url, name=faculty.name_campus, light=False)
    return [
        Cathedra(
            id_campus=f['Id'],
            name=f['ShortTitle'],
            name_campus=f['Name'],
            title=f['Title'],
            faculty=faculty
        )
        for f in res['Data']['Cathedras']
    ]


async def find_group(group_name):
    url = 'http://api.campus.kpi.ua/group/find'
    res = await _req(url, name=group_name)
    return [
        Group(
            id_campus=f['id'],
            name=f['name'],
            cathedra_id=f['cathedra']['id']
        )
        for f in res
    ]
