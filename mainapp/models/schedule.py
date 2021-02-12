from django.db import models
from .groups import Group, Cathedra


def _range2choices(start, stop):
    t = tuple(range(start, stop))
    return tuple(zip(t, t))


class Teacher(models.Model):
    url_rozklad = models.CharField(max_length=500, primary_key=True)
    name = models.CharField(max_length=500)
    full_name = models.CharField(max_length=500)
    cathedras = models.ManyToManyField(Cathedra, related_name='teachers')


class Room(models.Model):
    name = models.CharField(max_length=500, primary_key=True)
    lat = models.CharField(max_length=15, null=True)
    lon = models.CharField(max_length=15, null=True)


class Subject(models.Model):
    url_wiki = models.CharField(max_length=500, primary_key=True)
    name = models.CharField(max_length=500)


class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='lessons')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='lessons')

    lesson_type = models.CharField(max_length=50, null=True)

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='lessons')

    semestr = models.PositiveSmallIntegerField(choices=_range2choices(1, 2))
    week = models.PositiveSmallIntegerField(choices=_range2choices(1, 2))
    day = models.PositiveSmallIntegerField(choices=_range2choices(0, 6))
    num = models.PositiveSmallIntegerField(choices=_range2choices(0, 6))

    class Meta:
        unique_together = (
            ('group', 'semestr', 'week', 'day', 'num', 'subject', 'teacher'),
        )
