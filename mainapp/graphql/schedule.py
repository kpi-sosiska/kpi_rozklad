import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from mainapp import models


class Room(DjangoObjectType):
    class Meta:
        interfaces = (graphene.relay.Node,)
        model = models.Room


class Subject(DjangoObjectType):
    class Meta:
        interfaces = (graphene.relay.Node,)
        model = models.Subject
        filter_fields = ['name_normalized']


class Lesson(DjangoObjectType):
    class Meta:
        model = models.Lesson
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        filter_fields = ['semestr', 'week', 'day', 'num', ]



class ScheduleQuery(graphene.ObjectType):
    lesson = graphene.relay.Node.Field(Lesson)
    lessons = DjangoFilterConnectionField(Lesson)

    subject = graphene.relay.Node.Field(Subject)
    subjects = DjangoFilterConnectionField(Subject)
