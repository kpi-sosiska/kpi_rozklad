import re
from collections import namedtuple
from functools import cached_property

from django.db import models, transaction


class Faculty(models.Model):
    id_campus = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    name_campus = models.CharField(max_length=20)  # translit name
    title = models.CharField(max_length=500)

    def __str__(self):
        return f'{self.name} ({self.name_campus})'


class Cathedra(models.Model):
    id_campus = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)  # abbreviation + faculty
    name_short = models.CharField(max_length=20)  # abbreviation
    name_campus = models.CharField(max_length=20)  # == translit name
    title = models.CharField(max_length=500)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='cathedras')

    def __str__(self):
        return f'{self.name} ({self.name_campus})'


class Group(models.Model):
    uuid_rozklad = models.CharField(max_length=36, primary_key=True)
    id_campus = models.PositiveSmallIntegerField(null=True)
    name = models.CharField(null=True, max_length=500)  # name in campus
    name_rozklad = models.CharField(max_length=20)  # name in rozklad, maybe cathedra at the end
    cathedra = models.ForeignKey(Cathedra, null=True, on_delete=models.CASCADE, related_name='groups')

    RE_GROUP_CODE = re.compile(
        r'(\w{2,3})-'
        r'([зпвф]*)'
        r'(\d)(\d)'
        r'([мнпфі]*)'
        r'(-\d)?'
        r'(?: \((.*)\))?'
    )
    # todo understandable names (how?)
    GroupCode = namedtuple('GroupCode', ['prefix', 'm1', 'year', 'number', 'm2', 'm3', 'rozklad_cathedra'])

    def __str__(self):
        return f'{self.name_rozklad} ({self.name})'

    @property
    def url_rozklad(self):
        return "http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?v=" + self.uuid_rozklad

    @cached_property
    def _group_info(self):
        return self._parse_name(self.name)

    def prefix(self):
        return self._group_info.prefix

    def okr(self):
        # todo wrong
        r = self._group_info.m2
        if 'м' in r:
            return 'magister'
        if 'с' in r:
            return 'specialist'
        return 'bachelor'

    def type(self):
        # todo wrong
        if 'з' in self._group_info.m1:
            return 'extramural'
        return 'daily'

    def _rozklad_cathedra(self):
        return self._parse_name(self.name_rozklad).rozklad_cathedra

    @classmethod
    def _parse_name(cls, name):
        return cls.GroupCode(*cls.RE_GROUP_CODE.search(name).groups())

    def save_with_lessons(self, lessons):
        with transaction.atomic():
            self.save()
            self.lessons.all().delete()
            for lesson in lessons:
                lesson.teacher.save(update_fields=['name'])  # d on't delete teacher name_full when parse groups
                lesson.room.save()
                lesson.subject.save()
                lesson.group = self
                lesson.save()
