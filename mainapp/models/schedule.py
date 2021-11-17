from django.db import models
from .groups import Group, Cathedra


def _range2choices(start, stop):
    t = tuple(range(start, stop))
    return tuple(zip(t, t))


class Teacher(models.Model):
    POSITIONS_CHOICE = {
        'ас.': 'асистент',
        'доц.': 'доцент',
        'вик.': 'викладач',
        'ст.вик.': 'старший викладач',
        'проф.': 'професор',
        'зав.каф.': 'зав. кафедрою',
        'дек.': 'декан',
        # 'пос.': '',
    }

    uuid_rozklad = models.CharField(max_length=36, primary_key=True)
    position = models.CharField(max_length=10, choices=POSITIONS_CHOICE.items(), null=True)
    name = models.CharField(max_length=500)
    name_full = models.CharField(max_length=500, null=True, blank=True)
    cathedras_rozklad = models.CharField(max_length=500, null=True, blank=True)
    cathedras = models.ManyToManyField(Cathedra, related_name='teachers')

    @classmethod
    def create(cls, uuid_rozklad, name):
        name = name.removeprefix('пос.')
        position = None
        for pos in cls.POSITIONS_CHOICE:
            if name.startswith(pos):
                name = name.removeprefix(pos)
                position = pos
        return cls(uuid_rozklad=uuid_rozklad, name=name.strip(), position=position)

    @property
    def url_rozklad(self):
        return "http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?v=" + self.uuid_rozklad


class Room(models.Model):
    name = models.CharField(max_length=500, primary_key=True)
    lat = models.CharField(max_length=15, null=True)
    lon = models.CharField(max_length=15, null=True)


class Subject(models.Model):
    url_name = models.CharField(max_length=500, primary_key=True)
    name = models.CharField(max_length=500)
    name_normalized = models.CharField(max_length=500, null=True)

    @property
    def url_wiki(self):
        return "http://wiki.kpi.ua/index.php/" + self.url_name


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
