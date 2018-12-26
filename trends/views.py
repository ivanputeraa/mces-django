from django.shortcuts import render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

from .forms import *

from estimator.models import Machine_Yield_Rate_History, Maintenance_History

import datetime
import json

class TrendView(View):
    def get(self, request):
        form = TrendForm()
        return render(request, 'trends/trends-chart.html', {'form': form})

@csrf_exempt
def get_machine_trends_and_maintenance(request):
    if request.is_ajax():
        # Get data sent using ajax
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        machine = request.GET.get('machine', None)
        report_type = request.GET.get('report_type', None)

        # Convert str to datetime object
        date_format = '%Y-%m-%d'
        start_date = datetime.datetime.strptime(start_date_str, date_format)
        end_date = datetime.datetime.strptime(end_date_str, date_format)

        machine_yield_rates = Machine_Yield_Rate_History.objects \
            .values('period', 'yield_rate') \
            .filter(machine=machine, start_period__range=(start_date, end_date), end_period__range=(start_date, end_date), analyze_type=report_type) \
            .order_by('end_period')

        machine_maintenance = Maintenance_History.objects \
            .values('check_in_time', 'employee_id', 'operation_class', 'description', 'solution', 'reason') \
            .filter(machine=machine, check_in_time__range=(start_date, end_date)) \
            .order_by('check_in_time')

        period_date_dict = {}
        date_format = '%Y%m%d'
        for index, item in enumerate(machine_yield_rates):
            period = item['period'].split('_')
            period_date_dict[index] = {}
            period_date_dict[index]['start_period'] = datetime.datetime.strptime(period[0], date_format).date()
            period_date_dict[index]['end_period'] = datetime.datetime.strptime(period[1], date_format).date()

        maintenance_occurrence_dict = {};
        occurrence_counter = 0
        loop_counter = 0
        for key, value in period_date_dict.items():
            for item in list(machine_maintenance):
                if item['check_in_time'].date() >= value['start_period'] and item['check_in_time'].date() <= value['end_period']:
                    occurrence_counter = occurrence_counter + 1
            maintenance_occurrence_dict[loop_counter] = {}
            maintenance_occurrence_dict[loop_counter]['period'] = value['start_period'].strftime(date_format) + "_" + value['end_period'].strftime(date_format)
            maintenance_occurrence_dict[loop_counter]['occurrence'] = occurrence_counter
            occurrence_counter = 0
            loop_counter += loop_counter + 1

        result = json.dumps({
            'yield_rate': list(machine_yield_rates),
            'maintenance_history': maintenance_occurrence_dict,
        })

        return JsonResponse(result, content_type='application/json', safe=False)

@csrf_exempt
def machine_autocomplete(request):
    if request.is_ajax():
        machine = request.GET.get('search', None)
        queryset = Machine_Yield_Rate_History.objects.filter(machine__startswith=machine)

        # Because MySQL db backend doesn't support DISTINCT ON syntax,
        # so manually filter duplicate machine names from the queryset
        temp_items = []
        machines = []
        for item in queryset:
            if item.machine not in machines:
                temp_items.append(item)
                machines.append(item.machine)

        data = {
            'list': machines,
        }
        return JsonResponse(data)