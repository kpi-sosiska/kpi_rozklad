import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kpi_rozklad.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

django.setup()

from parserapp.parser.campus.groups import get_cathedras, get_faculties, find_group
from parserapp.parser.campus.disciplines import get_disciplines
from parserapp.parser.rozklad.group import get_group
from parserapp.parser.rozklad.groups import get_groups_list
