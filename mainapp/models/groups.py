import re
from collections import namedtuple
from functools import cached_property

from django.db import models


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
    id_campus = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=500)  # name in campus
    name_rozklad = models.CharField(max_length=20)  # name in rozklad, maybe cathedra at the end
    url_rozklad = models.CharField(max_length=500)
    cathedra = models.ForeignKey(Cathedra, on_delete=models.CASCADE, related_name='groups')

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





