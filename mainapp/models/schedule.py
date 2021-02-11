from django.db import models
from .groups import Group


def _range2choices(start, stop):
    t = tuple(range(start, stop))
    return tuple(zip(t, t))


class Teacher(models.Model):
    url_rozklad = models.CharField(max_length=500, primary_key=True)
    name = models.CharField(max_length=500)


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

    lesson_semestr = models.PositiveSmallIntegerField(choices=_range2choices(1, 2))
    lesson_week = models.PositiveSmallIntegerField(choices=_range2choices(1, 2))
    lesson_day = models.PositiveSmallIntegerField(choices=_range2choices(0, 6))
    lesson_num = models.PositiveSmallIntegerField(choices=_range2choices(0, 6))

    class Meta:
        unique_together = (
            ('group', 'lesson_semestr', 'lesson_week', 'lesson_day', 'lesson_num', 'subject'),
        )
