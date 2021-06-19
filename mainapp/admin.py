from django.contrib import admin

from mainapp.models import Cathedra, Faculty, Group, Lesson, Room, Subject, Teacher


for model in (Faculty, Cathedra, Group, Teacher, Room, Subject, Lesson):
    admin.site.register(model)

