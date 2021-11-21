import graphene

from mainapp.graphql.groups import GroupQuery
from mainapp.graphql.schedule import ScheduleQuery


class Query(GroupQuery, ScheduleQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
