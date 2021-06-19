import os
import re
import csv
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kpi_rozklad.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

django.setup()

from mainapp.models.schedule import Teacher
from mainapp.models.schedule import Group
from mainapp.models.groups import Faculty
from mainapp.models.groups import Cathedra

# Export teachers
with open('mainapp_teacher.csv', mode='w') as csvfile:

    is_eng_re = re.compile(r"інозем|іншомов|ін\. мова", flags=re.IGNORECASE)
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['id', 'name', 'is_eng', 'lessons'])
    for teacher in Teacher.objects.all():
        lessons = ', '.join(sorted(teacher.lessons.all()))
        is_eng = is_eng_re.findall(lessons)

        writer.writerow([teacher.url_rozklad, teacher.name, is_eng, lessons])

# Export faculties
with open('mainapp_faculty.csv', mode='w') as csvfile:

    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['id', 'name'])
    for faculty in Faculty.objects.all():
        writer.writerow([faculty.id_campus, faculty.name])


# Export cathedras
with open('mainapp_cathedra.csv', mode='w') as csvfile:

    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['id', 'name', 'faculty_id'])
    for cathedra in Cathedra.objects.all():
        writer.writerow([cathedra.id_campus, cathedra.name, cathedra.faculty])

# Export groups
with open('mainapp_group.csv', mode='w') as csvfile:

    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['id', 'name', 'cathedra_id'])
    for group in Group.objects.all():
        writer.writerow([group.id_campus, group.name, group.cathedra_id])

with open('mainapp_group.csv', mode='w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['id', 'name', 'cathedra_id'])
    for group in Group.objects.all():
        writer.writerow([group.id_campus, group.name, group.cathedra_id])