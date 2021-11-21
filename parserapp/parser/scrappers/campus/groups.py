
from mainapp.models import Faculty, Cathedra, Group, Teacher
from parserapp.parser.scrappers.campus.utils import _req




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



async def get_teachers(teacher_name):
    url = 'http://api.campus.kpi.ua/Intellect/Find'
    res = await _req(url, value=teacher_name, pageSize=1000)

    teachers = []
    for f in res['Data']:
        cathedras = [p['Subdivision']['Id'] for p in f['Positions']]
        id_campus = int(f['Photo'].split("https://api.campus.kpi.ua/Account/")[1].split("/ProfileImage")[0])
        t = Teacher(
            id_campus=id_campus,
            slug_campus=f['UserIdentifier'],
            name_campus=f['FullName'],
        )
        t._catherdas = cathedras
        teachers.append(t)

    return teachers
