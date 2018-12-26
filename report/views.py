from django.urls import reverse_lazy
from django.views.generic import *

from .forms import *


class ReportDownload(FormView):
    form_class = ReportForm
    template_name = 'report/report-download.html'
    success_url = reverse_lazy('estimator:report-download')
