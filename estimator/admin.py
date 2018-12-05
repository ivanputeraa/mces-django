from django.contrib import admin

from .models import *

admin.site.register(GBOM)
admin.site.register(LOT)
admin.site.register(Machine)
admin.site.register(Report)
admin.site.register(File)