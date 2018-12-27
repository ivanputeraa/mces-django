from django.conf.urls import re_path

from . import views

app_name = 'report'

urlpatterns = [
    re_path(r'^download/$', views.ReportDownload.as_view(), name='download-page'),
    re_path(r'^download/report/$', views.download, name='download'),
]
