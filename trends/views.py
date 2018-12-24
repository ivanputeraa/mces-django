from django.shortcuts import render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

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

        # Get week number
        start_week = start_date.isocalendar()[1]
        end_week = end_date.isocalendar()[1]

        machine_yield_rates = Machine_Yield_Rate_History.objects\
            .values('period', 'yield_rate')\
            .filter(machine=machine, start_period__range=(start_date, end_date), end_period__range=(start_date, end_date), analyze_type=report_type)\
            .order_by('end_period')

        yield_rate_data = []
        for item in machine_yield_rates:
            yield_rate_data.append(item)

        machine_yield_rate_periods = Machine_Yield_Rate_History.objects \
            .values('start_period', 'end_period') \
            .filter(machine=machine, start_period__range=(start_date, end_date),
                    end_period__range=(start_date, end_date), analyze_type=report_type) \
            .order_by('end_period')

        machine_maintenance = Maintenance_History.objects\
            .values('check_in_time')\
            .filter(machine=machine, check_in_time__range=(start_date, end_date), check_out_time__range=(start_date, end_date))\
            .order_by('check_in_time')

        start_period_array = []
        end_period_array = []
        for item in machine_yield_rate_periods:
            start_period_array.append(item['start_period'])
            end_period_array.append(item['end_period'])

        maintenance_check_in_date = []
        for item in machine_maintenance:
            maintenance_check_in_date.append(item['check_in_time'].date())

        maintenance_list = []
        for item in maintenance_check_in_date:
            for index, start_period in enumerate(start_period_array):
                if item > start_period_array[index] and item < end_period_array[index]:
                    maintenance_list.append(item)

        # # Count machine occurrences which has the same check_in_week
        # distinct_machine_maintenance = collections.Counter(item['check_in_week'] for item in list(machine_maintenance))
        #
        # # Map distinct_machine_maintenance into an array of dictionaries
        # maintenance_data = []
        # for key, value in distinct_machine_maintenance.items():
        #     maintenance_data.append({'check_in_week': key, 'occurrence': value})
        #
        # # Sort maintenance_data by check_in_week
        # sorted_maintenance_data = sorted(list(maintenance_data), key=itemgetter('check_in_week'))
        # print(sorted_maintenance_data)

        response = json.dumps({
            'yield_rate': list(machine_yield_rates),
            # 'maintenance_history': list(machine_maintenance),
        })

        return JsonResponse(response, content_type='application/json', safe=False)

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

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