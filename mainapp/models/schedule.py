from django.db import models
from .groups import Group


def _range2choices(start, stop):
    t = tuple(range(start, stop))
    return tuple(zip(t, t))


class Teacher(models.Model):
    url_rozklad = models.CharField(max_length=500)
    name = models.CharField(max_length=500)


class Room(models.Model):
    url_maps = models.CharField(max_length=500)
    name = models.CharField(max_length=500)


class Subject(models.Model):
    url_wiki = models.CharField(max_length=500)
    name = models.CharField(max_length=500)


class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    lesson_semestr = models.PositiveSmallIntegerField(choices=_range2choices(1, 2))
    lesson_week = models.PositiveSmallIntegerField(choices=_range2choices(1, 2))
    lesson_day = models.PositiveSmallIntegerField(choices=_range2choices(0, 6))
    lesson_num = models.PositiveSmallIntegerField(choices=_range2choices(0, 6))

