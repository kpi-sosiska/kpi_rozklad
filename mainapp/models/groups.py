import re
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
    def _parse(self):
        return list(GROUP_CODE_RE.search(self.name_rozklad).groups())

    def prefix(self):
        return self._parse[0]

    def okr(self):
        # todo wrong
        r = self._parse[1]
        if 'м' in r:
            return 'magister'
        if 'с' in r:
            return 'specialist'
        return 'bachelor'

    def type(self):
        if 'з' in self._parse[1]:
            return 'extramural'
        return 'daily'

    def cathedra_rozklad(self):
        return self._parse[6]



