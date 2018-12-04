from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.views.generic import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .forms import *
from .models import *
from datetime import datetime

import datetime
import pandas as pd

class IndexView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return redirect('estimator:home')

class HomeView(View):
    def get(self, request):
        return render(request, 'estimator/home.html')

# BEGIN File Upload Views
class FileList(ListView):
    model = File
    template_name_suffix = '-list'
    queryset = File.objects.all().order_by('last_modified')

@login_required
def file_create(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_type = form.cleaned_data['type']
            instances = []
            df = pd.read_csv(file, encoding='big5', header=0)

            if file_type == 0:
                if 'BADNUM' not in df.columns.values:
                    messages.error(request,
                                   'The chosen file is not a valid production data file.',
                                   extra_tags='alert')
                    return render(request, 'estimator/file-create.html', {'form': form})
                else:
                    part_number = df['料號'].values.copy()
                    check_in_time = df['CHECK IN TIME'].values.copy()
                    gbom = df['GBOM'].values.copy()
                    lot_number = df['批號'].values.copy()
                    station_number = df['站別次序'].values.copy()
                    station = df['站別'].values.copy()
                    station_name = df['站別名稱'].values.copy()
                    machine_number = df['機器編號'].values.copy()

                    for counter in range(0, len(df)):  # Exclude last row
                        instance = Production_Data_By_Time(
                            part_number=str(part_number[counter]),
                            check_in_time=str(check_in_time[counter]).replace('/', '-'),
                            gbom=str(gbom[counter]),
                            lot_number=str(lot_number[counter]),
                            station_number=str(station_number[counter]),
                            station=str(station[counter]),
                            station_name=str(station_name[counter]),
                            machine_number=str(machine_number[counter]),
                        )
                        instances.append(instance)
                    Production_Data_By_Time.objects.bulk_create(instances)

            if file_type == 1:
                if 'BADNUM' not in df.columns.values:
                    messages.error(request,
                                   'The chosen file is not a valid production data file.',
                                   extra_tags='alert')
                    return render(request, 'estimator/file-create.html', {'form': form})
                else:
                    part_number = df['料號'].values.copy()
                    check_in_time = df['CHECK IN TIME'].values.copy()
                    gbom = df['GBOM'].values.copy()
                    lot_number = df['批號'].values.copy()
                    station_number = df['站別次序'].values.copy()
                    station = df['站別'].values.copy()
                    station_name = df['站別名稱'].values.copy()
                    machine_number = df['機器編號'].values.copy()

                    for counter in range(0, len(df)):  # Exclude last row
                        instance = Production_Data_By_Warehouse(
                            part_number=str(part_number[counter]),
                            check_in_time=str(check_in_time[counter]).replace('/', '-'),
                            gbom=str(gbom[counter]),
                            lot_number=str(lot_number[counter]),
                            station_number=str(station_number[counter]),
                            station=str(station[counter]),
                            station_name=str(station_name[counter]),
                            machine_number=str(machine_number[counter]),
                        )
                        instances.append(instance)
                    Production_Data_By_Warehouse.objects.bulk_create(instances)

            if file_type == 2:  # Maintenance History file type
                if '大項故障代碼' not in df.columns.values:
                    messages.error(request,
                                   'The chosen file is not a valid maintenance history file.',
                                   extra_tags='alert')
                    return render(request, 'estimator/file-create.html', {'form': form})
                else:
                    machine_list = df['設備代碼'].values.copy()
                    check_in_time_list = df['CHECK IN TIME'].values.copy()
                    employee_id_list = df['員工代碼'].values.copy()
                    operation_class_list = df['作業類別'].values.copy()
                    major_code_list = df['大項故障代碼'].values.copy()
                    major_desc_list = df['大項故障名稱'].values.copy()
                    minor_code_list = df['小項故障代碼'].values.copy()
                    minor_desc_list = df['小項故障代碼說明'].values.copy()
                    description_list = df['描述 異常 / 故障現象 '].values.copy()
                    solution_list = df['對策 異常/故障解決'].values.copy()
                    reason_list = df['分析 異常/故障原因'].values.copy()
                    replace_parts_list = df['備品需求'].values.copy()

                    for counter in range(0, len(df) - 1):  # Exclude last row
                        instance = Maintenance_History(
                            machine=str(machine_list[counter]),
                            check_in_time=str(check_in_time_list[counter]).replace('/', '-'),
                            employee_id=str(employee_id_list[counter]).replace('.0', ''),
                            operation_class=str(operation_class_list[counter]),
                            major_code=str(major_code_list[counter]),
                            major_desc=str(major_desc_list[counter]),
                            minor_code=str(minor_code_list[counter]),
                            minor_desc=str(minor_desc_list[counter]),
                            description=str(description_list[counter]),
                            solution=str(solution_list[counter]),
                            reason=str(reason_list[counter]),
                            replace_parts=str(replace_parts_list[counter])
                        )
                        instances.append(instance)
                    Maintenance_History.objects.bulk_create(instances)

            if file_type == 3:
                if 'DEFECT CATEGORY' not in df.columns.values:
                    messages.error(request,
                                   'The chosen file is not a valid bad phenomenon file.',
                                   extra_tags='alert')
                    return render(request, 'estimator/file-create.html', {'form': form})
                else:
                    lot_number = df['批號'].values.copy()
                    check_in_time = df['生產結束日期'].values.copy()
                    defect_category = df['DEFECT CATEGORY'].values.copy()

                    for counter in range(0, len(df)):  # Exclude last row
                        instance = Bad_Phenomenon_By_Time(
                            lot_number=str(lot_number[counter]),
                            check_in_time=str(check_in_time[counter]).replace('/', '-'),
                            defect_category=str(defect_category[counter])
                        )
                        instances.append(instance)
                    Bad_Phenomenon_By_Time.objects.bulk_create(instances)

            if file_type == 4:
                if 'DEFECT CATEGORY' not in df.columns.values:
                    messages.error(request,
                                   'The chosen file is not a valid bad phenomenon file.',
                                   extra_tags='alert')
                    return render(request, 'estimator/file-create.html', {'form': form})
                else:
                    lot_number = df['批號'].values.copy()
                    check_in_time = df['生產結束日期'].values.copy()
                    defect_category = df['DEFECT CATEGORY'].values.copy()

                    for counter in range(0, len(df)):  # Exclude last row
                        instance = Bad_Phenomenon_By_Warehouse(
                            lot_number=str(lot_number[counter]),
                            defect_category=str(defect_category[counter]),
                            check_in_time=str(check_in_time[counter]).replace('/', '-'),
                        )
                        instances.append(instance)
                    Bad_Phenomenon_By_Warehouse.objects.bulk_create(instances)

            if file_type == 5:
                if '自製/委外' not in df.columns.values:
                    messages.error(request,
                                   'The chosen file is not a valid GBOM file.',
                                   extra_tags='alert')
                    return render(request, 'estimator/file-create.html', {'form': form})
                else:
                    gbom = df['GBOM'].values.copy()
                    station = df['站別'].values.copy()
                    station_number = df['次序'].values.copy()
                    outsourcing = df['自製/委外'].values.copy()
                    station_class = df['類別'].values.copy()
                    station_name = df['中文名稱'].values.copy()

                    for counter in range(0, len(df)):  # Exclude last row
                        instance = GBOM(
                            gbom=str(gbom[counter]),
                            station=str(station[counter]),
                            station_number=str(station_number[counter]),
                            outsourcing=str(outsourcing[counter]).encode('big5').decode('unicode-escape'),
                            station_class=str(station_class[counter]).encode('big5').decode('unicode-escape'),
                            station_name=str(station_name[counter]).encode('big5').decode('unicode-escape'),
                        )
                        instances.append(instance)
                    GBOM.objects.bulk_create(instances)

            form.save()
            return HttpResponseRedirect(reverse('estimator:file-list'))
        else:
            messages.warning(request, 'Please correct the error below.')
    else: # request.method == 'GET':
        form = FileForm()
    return render(request, 'estimator/file-create.html', {'form': form})

class FileUpdate(UpdateView):
    model = File
    form_class = FileForm
    template_name_suffix = '-update'
    success_url = reverse_lazy('estimator:file-list')

# Display a confirmation warning before deleting, if triggered with GET: it shows the warning(template view)
# If triggered with POST then deletes, the template will receive object, which is the item to be deleted
class FileDelete(DeleteView):
    model = File
    template_name_suffix = '-delete'
    success_url = reverse_lazy('estimator:file-list')

    # Notice get_success_url is defined here and not in the model, because the model will be deleted
    def get_success_url(self):
        return reverse('estimator:file-list')
# END File Upload Views

# BEGIN Report Views
class ReportList(ListView):
    model = Report
    template_name_suffix = '-list'
    queryset = Report.objects.all()

# END Report Views

class TrendView(View):
    def get(self, request):
        form = TrendForm()
        return render(request, 'estimator/trend.html', {'form': form})

@csrf_exempt
def get_machine_trends(request):
    if request.is_ajax():
        # Get data sent using ajax
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        machine = request.GET.get('machine', None)
        is_panels = request.GET.get('is_panels', None)

        # Convert str to datetime object
        date_format = '%Y-%m-%d'
        start_date = datetime.datetime.strptime(start_date_str, date_format)
        end_date = datetime.datetime.strptime(end_date_str, date_format)

        # Get week number
        start_week = start_date.isocalendar()[1]
        end_week = end_date.isocalendar()[1]

        machine_trends = Report.objects.filter(machine=machine, week__range=(start_week, end_week), is_panels=is_panels) \
            .order_by('week') \
            .values('week','yield_rate')

        if machine_trends:
            response = list(machine_trends)
            return JsonResponse(response, safe=False)

def machine_autocomplete(request):
    if request.is_ajax():
        queryset = Machine.objects.filter(machine__startswith=request.GET.get('search', None))
        list = []
        for i in queryset:
            list.append(i.machine)
        data = {
            'list': list,
        }
        return JsonResponse(data)