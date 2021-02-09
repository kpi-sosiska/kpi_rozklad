import re
from collections import namedtuple
from functools import cached_property

from django.db import models


GROUP_CODE_RE = re.compile(
    r'(.*)-'
    r'([зпвф]*)'
    r'(\d)(\d)'
    r' ?([мнпф]*)'
    r'(.*?)'
    r'(?:\((\S+)\))?'
)
GroupCode = namedtuple('GroupCode', ['prefix', 'm1', 'year', 'number', 'm2', 'm3', 'rozklad_cathedra'])


class Faculty(models.Model):
    id_campus = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=20)
    name_campus = models.CharField(max_length=20)
    title = models.CharField(max_length=500)


class Cathedra(models.Model):
    id_campus = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=20)
    name_campus = models.CharField(max_length=20)
    title = models.CharField(max_length=500)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)


class Group(models.Model):
    id_campus = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=500)
    name_rozklad = models.CharField(max_length=20)
    url_rozklad = models.CharField(max_length=500)
    cathedra = models.ForeignKey(Cathedra, on_delete=models.CASCADE)

    @cached_property
    def _group_info(self):
        return GroupCode(*GROUP_CODE_RE.search(self.name_rozklad).groups())

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



