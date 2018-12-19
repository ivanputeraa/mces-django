from django.conf import settings
from django.conf.urls import url, include, re_path
from django.conf.urls.static import static

from . import views

app_name = 'estimator'

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^home/$', views.HomeView.as_view(), name='home'),

    # Machine Yield Rate and Maintenance Trend Page URL
    re_path(r'^trend/$', views.TrendView.as_view(), name='trend'),

    # File Upload Page URLs
    re_path(r'^file/list/$', views.FileList.as_view(), name='file-list'),
    re_path(r'^file/create/$', views.file_create, name='file-create'),
    re_path(r'^file/update/(?P<pk>\d+)/$', views.FileUpdate.as_view(), name='file-update'),
    re_path(r'^file/delete/(?P<pk>\d+)/$', views.FileDelete.as_view(), name='file-delete'),
    re_path(r'^file/analyze/(?P<pk>\d+)/$', views.analyze_data, name='file-analyze'),

    # Report Page URLs
    re_path(r'^report/download/$', views.ReportDownload.as_view(), name='report-download'),

    # Query Production Data Page URL
    re_path(r'^query-production-data/$', views.ProductionDataQuery.as_view(), name='query-production-data'),

    # AJAX URLs
    re_path(r'^ajax/get-machine-trends/$', views.get_machine_trends_and_maintenance, name='get-machine-trends-and-maintenance'),
    re_path(r'^ajax/machine-autocomplete/$', views.machine_autocomplete, name='machine-autocomplete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)