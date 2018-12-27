from django.urls import reverse_lazy
from django.views.generic import *
from django.shortcuts import reverse, HttpResponseRedirect

from .forms import *

import os
import pandas as pd


class ReportDownload(FormView):
    form_class = ReportForm
    template_name = 'report/report-download.html'
    success_url = reverse_lazy('report:download-page')


def download(request):
    if request.method == 'POST':
        period = request.POST['period']
        report_data = Machine_Yield_Rate_History.objects.values_list('machine', 'yield_rate', 'processed_pieces', 'analyze_type')\
            .filter(period=period).order_by('analyze_type', 'yield_rate')

        # Convert django queryset to pandas dataframe structure
        df = pd.DataFrame(list(report_data))
        file_path = 'report/temp_report_file/' + period + '_report.csv'

        # Remove previous report file
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("The file does not exist")

        df.to_csv(file_path, sep='\t', encoding='utf-8')

        return HttpResponseRedirect(reverse('estimator:home'))




