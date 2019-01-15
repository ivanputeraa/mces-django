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

        # Convert django queryset to pandas data frame structure
        df = pd.DataFrame(list(report_data))
        df.columns = ['Machine', 'Estimated Yield Rate', 'Bad Pieces', 'Type']
        df.sort_values('Estimated Yield Rate')
        machine_list = df['Machine'].values.copy()
        yield_rate_list = df['Estimated Yield Rate'].values.copy()
        bad_pieces_list = df['Bad Pieces'].values.copy()
        type_list = df['Type'].values.copy()

        if report_type == 'Cell':
            file_name = period + '_cell_based_report.csv'
        elif report_type == 'Panel':
            file_name = period + '_panel_based_report.csv'

        file_path = settings.MEDIA_ROOT + 'reports/' + file_name

        # Remove previous report file
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("The file does not exist")

        # Write data frame into csv
        # Change with universal format (,)
        with open(file_path, 'w') as file_output:
            file_output.write(',Machine,Estimated Yield Rate,Bad Pieces,Type\n')
            for counter in range(0, machine_list.size):
                # print('   %.5f %.3f %s'%(p[order[i]],bad_pieces_estimation_value[order[i]],machine_name[order[i]]))
                file_output.write(str(counter + 1))
                file_output.write(',')
                file_output.write(str(machine_list[counter]))
                file_output.write(',')
                file_output.write(str(yield_rate_list[counter]))
                file_output.write(',')
                file_output.write(str(bad_pieces_list[counter]))
                file_output.write(',')
                file_output.write(str(type_list[counter]))
                file_output.write('\n')
        # df.to_csv(file_path, sep='\t', encoding='utf-8')

        # Source:https://stackoverflow.com/questions/2294507/how-to-return-static-files-passing-through-a-view-in-django
        # Read the csv file
        location = file_path
        file = open(location, 'rb')
        content = file.read()
        file.close

        # Serve the file
        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + file_name
        return response




