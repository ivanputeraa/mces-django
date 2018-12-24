from django.conf.urls import re_path

from . import views

app_name = 'trends'

urlpatterns = [
    re_path(r'^trend/$', views.TrendView.as_view(), name='yield-rate-maintenance-chart'),

    # AJAX URLs
    re_path(r'^ajax/get-machine-trends/$', views.get_machine_trends_and_maintenance,
            name='get-machine-trends-and-maintenance'),
    re_path(r'^ajax/machine-autocomplete/$', views.machine_autocomplete, name='machine-autocomplete'),
]