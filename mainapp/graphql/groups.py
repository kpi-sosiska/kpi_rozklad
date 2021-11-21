import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from mainapp import models
from mainapp.graphql.schedule import Lesson


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
        interfaces = (graphene.relay.Node,)
        model = models.Faculty
        filter_fields = ['name']



class Cathedra(DjangoObjectType):
    class Meta:
        interfaces = (graphene.relay.Node,)
        model = models.Cathedra
        filter_fields = ['name_short']



class Teacher(DjangoObjectType):
    class Meta:
        interfaces = (graphene.relay.Node,)
        model = models.Teacher
        filter_fields = ['name', 'name_full', 'uuid_rozklad', 'position', ]



class GroupQuery(graphene.ObjectType):
    group = graphene.relay.Node.Field(Group)
    groups = DjangoFilterConnectionField(Group)

    teacher = graphene.relay.Node.Field(Teacher)
    teachers = DjangoFilterConnectionField(Teacher)

    faculty = graphene.relay.Node.Field(Faculty)
    faculties = DjangoFilterConnectionField(Faculty)

    cathedra = graphene.relay.Node.Field(Cathedra)
    cathedras = DjangoFilterConnectionField(Cathedra)



