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
    is_eng_re = re.compile(r"інозем|іншомов|ін\. мова|англійська", flags=re.IGNORECASE)
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['id', 'name', 'photo', 'is_eng', 'cathedras', 'lessons', 'univer_id', 'slug'])
    for teacher in Teacher.objects.all():
        lessons = teacher.lessons.filter(subject__isnull=False).values_list('subject__name_normalized', flat=True).distinct()
        lessons = '\n'.join(sorted(lessons))
        is_eng = int(bool(is_eng_re.findall(lessons)))
        photo = f'https://api.campus.kpi.ua/Account/{teacher.id_campus}/ProfileImage' if teacher.id_campus else None

        writer.writerow([teacher.uuid_rozklad, teacher.name_full, photo, is_eng, teacher.cathedras_rozklad, lessons, 1, teacher.slug_campus])

# Export faculties
with open('mainapp_faculty.csv', mode='w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['id', 'name'])
    for faculty in Faculty.objects.all():
        writer.writerow([faculty.id_campus, faculty.name])

# Export groups
with open('mainapp_group.csv', mode='w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['id', 'name', 'faculty_id'])
    for group in Group.objects.all():
        fid = group.cathedra.faculty_id if group.cathedra else None
        writer.writerow([group.uuid_rozklad, group.name_rozklad, fid])

# Export teacherngroup
with open('mainapp_teacherngroup.csv', mode='w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    counter = 0

    writer.writerow(['id', 'group_id', 'teacher_id'])
    r = Group.objects.filter(lessons__semestr=1).values_list('uuid_rozklad', 'lessons__teacher_id').distinct()
    for group_id, teacher_id in r:
        counter += 1
        writer.writerow([counter, group_id, teacher_id])

