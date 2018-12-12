from django.contrib import admin

from .models import *

admin.site.register(File)
admin.site.register(GBOM)
admin.site.register(LOT)
admin.site.register(Machine)
admin.site.register(Report)
admin.site.register(Maintenance_History)
admin.site.register(Production_Data_By_Warehouse)
admin.site.register(Production_Data_By_Time)
admin.site.register(Bad_Phenomenon_By_Warehouse)
admin.site.register(Bad_Phenomenon_By_Time)
admin.site.register(Machine_Yield_Rate_History)