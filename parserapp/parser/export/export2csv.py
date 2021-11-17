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

    writer.writerow(['uuid', 'name', 'is_eng', 'lessons'])
    for teacher in Teacher.objects.all():
        lessons = teacher.lessons.all().values_list('subject__name_normalized', flat=True).distinct()
        lessons = '\n'.join(sorted(lessons))
        is_eng = int(bool(is_eng_re.findall(lessons)))

        writer.writerow([teacher.uuid_rozklad, teacher.name_full, is_eng, teacher.cathedras_rozklad, lessons])

# Export faculties
with open('mainapp_faculty.csv', mode='w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['id', 'name'])
    for faculty in Faculty.objects.all():
        writer.writerow([faculty.id_campus, faculty.name])

# Export groups
with open('mainapp_group.csv', mode='w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['uuid', 'name', 'faculty_id'])
    for group in Group.objects.all():
        fid = group.cathedra.faculty_id if group.cathedra else None
        writer.writerow([group.uuid_rozklad, group.name_rozklad, fid])

# Export teacherngroup
with open('mainapp_teacherngroup.csv', mode='w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['group_id', 'teacher_id'])
    r = Group.objects.filter(lessons__semestr=2).values_list('uuid_rozklad', 'lessons__teacher_id').distinct()
    for group_id, teacher_id in r:
        writer.writerow([group_id, teacher_id])

