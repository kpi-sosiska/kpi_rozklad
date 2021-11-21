from mainapp.models import Cathedra, Faculty, Group, Lesson, Room, Subject, Teacher

models = [Cathedra, Faculty, Group, Lesson, Room, Subject, Teacher]


def reset():
    print("reset")

    for m in models:
        m.objects.all().delete()
