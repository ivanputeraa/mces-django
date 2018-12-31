import django_tables2 as tables
from .models import *

class MachineTables(tables.Table):
    class Meta:
        model = Machine
        template_name = 'django_tables2/bootstrap.html'