import re
from collections import namedtuple
from functools import cached_property

from django.db import models


GROUP_CODE_RE = re.compile(
    r'(\w{2,3})-'
    r'([зпвф]*)'
    r'(\d)(\d)'
    r'([мнпфі]*)'
    r'(-\d)?'
    r'(?: \((.*)\))?'
)
# todo understandable names (how?)
GroupCode = namedtuple('GroupCode', ['prefix', 'm1', 'year', 'number', 'm2', 'm3', 'rozklad_cathedra'])


class Faculty(models.Model):
    id_campus = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    name_campus = models.CharField(max_length=20)
    title = models.CharField(max_length=500)

    def __str__(self):
        return f'{self.name} ({self.name_campus})'


class Cathedra(models.Model):
    id_campus = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    name_campus = models.CharField(max_length=20)
    title = models.CharField(max_length=500)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} ({self.name_campus})'


class Group(models.Model):
    id_campus = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=500)
    name_rozklad = models.CharField(max_length=20)
    url_rozklad = models.CharField(max_length=500)
    cathedra = models.ForeignKey(Cathedra, on_delete=models.CASCADE)

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
        return GroupCode(*GROUP_CODE_RE.search(name).groups())





