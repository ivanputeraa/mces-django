from django.urls import reverse_lazy
from django.views.generic import *
from django.shortcuts import HttpResponse
from django.conf import settings

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
        report_type = request.POST['report_type']
        report_data = Machine_Yield_Rate_History.objects.values_list('machine', 'yield_rate', 'processed_pieces',
                                                                     'analyze_type')\
            .filter(period=period, analyze_type=report_type).order_by('yield_rate')

        # Convert django queryset to pandas dataframe structure
        df = pd.DataFrame(list(report_data))
        df.columns = ['Machine', 'Estimated Yield Rate', 'Bad Pieces', 'Type']

        if report_type == 'Cell':
            file_path = settings.MEDIA_ROOT + 'reports/' + period + '_cell_based_report.csv'
        elif report_type == 'Panel':
            file_path = settings.MEDIA_ROOT + 'reports/' + period + '_panel_based_report.csv'

        # Remove previous report file
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("The file does not exist")

        # Write dataframe into csv
        df.to_csv(file_path, sep='\t', encoding='utf-8')

        # Source : https://stackoverflow.com/questions/2294507/how-to-return-static-files-passing-through-a-view-in-django
        # Read the csv file
        location = file_path
        file = open(location, 'rb')
        content = file.read()
        file.close

        # Serve the file
        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + period + '.csv'

        return response




