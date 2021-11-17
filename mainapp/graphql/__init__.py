import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from mainapp import models


class Group(DjangoObjectType):
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


class Lesson(DjangoObjectType):
    class Meta:
        model = models.Lesson
        convert_choices_to_enum = False


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
