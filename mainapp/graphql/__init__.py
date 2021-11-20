import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from mainapp import models


class Lesson(DjangoObjectType):
    class Meta:
        model = models.Lesson
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        filter_fields = ['semestr', 'week', 'day', 'num', ]


class Group(DjangoObjectType):
    lesson_ = DjangoFilterConnectionField(Lesson)

    prefix = graphene.String(source='prefix')
    okr = graphene.String(source='okr')
    type = graphene.String(source='type')

    class Meta:
        model = models.Group
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }


class Faculty(DjangoObjectType):
    class Meta:
        model = models.Faculty


class Cathedra(DjangoObjectType):
    class Meta:
        model = models.Cathedra


class Teacher(DjangoObjectType):
    class Meta:
        model = models.Teacher


class Room(DjangoObjectType):
    class Meta:
        model = models.Room


class Subject(DjangoObjectType):
    class Meta:
        model = models.Subject


class Query(graphene.ObjectType):
    group = graphene.relay.Node.Field(Group)
    groups = DjangoFilterConnectionField(Group)


schema = graphene.Schema(query=Query)
