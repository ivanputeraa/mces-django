from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.views.generic import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Count
from django.conf import settings

from .forms import *
from .models import *
from datetime import datetime
from operator import itemgetter

from shutil import copyfile
from estimator import DataPreprocess
from estimator import EM_Algorithm2
from estimator import LinearLeastSquaresToSolveWeeklyYield

import datetime
import pandas as pd
import json
import collections
import os
import time

# Begin of PeiKai's code
def analyze_data(request, pk): # Rename from UploadAndAnalyze

    file = File.objects.values_list('file', flat=True).filter(pk=pk)
    file_path = os.path.join(settings.MEDIA_ROOT, file[0])

    # return HttpResponse(os.path.join(settings.MEDIA_ROOT, file_path))

    # Read the prod data file
    DataFlow = pd.read_csv(file_path, encoding='big5')

    # Check whether prod data is the correct one
    if '入庫日期' not in DataFlow.columns.values:
        return HttpResponse('production data is wrong')
    else:  # 根据入库时间重命名
        FinishTimeList = DataFlow['入庫日期'].values.copy()
        FinishTimeList.sort()
        FinishTimeRange = FinishTimeList[0] + "_" + FinishTimeList[len(FinishTimeList) - 1]
        FinishTimeRange = FinishTimeRange.replace("/", "_")

        # RawDataPath = os.path.join(os.getcwd() + "\\analyse\\RawData", FinishTimeRange + "_RawData.csv")
        RawDataPath = os.path.join(os.getcwd() + "/estimator/RawData", FinishTimeRange + "_RawData.csv")

        ProcessedDataPath = os.path.join(os.getcwd() + "/estimator/ProcessedData", FinishTimeRange + "_ProcessedData.csv")
        ProcessedDataPathByCellNotSplit = ProcessedDataPath.replace("ProcessedData.csv", "ProcessedDataByCellNotSplit.csv")
        ProcessedDataPathByPanelNotSplit = ProcessedDataPath.replace("ProcessedData.csv", "ProcessedDataByPanelNotSplit.csv")

        ReportPath = os.path.join(os.getcwd() + "/estimator/Report", FinishTimeRange + "_Report.csv")
        ReportPathByCellNotSplit = ReportPath.replace("Report.csv", "ReportByCellNotSplit.csv")
        ReportPathByPanelNotSplit = ReportPath.replace("Report.csv", "ReportByPanelNotSplit.csv")

        copyfile(file_path, RawDataPath)

        # Data pre processing
        DataPreprocess.ProcessData(RawDataPath, ProcessedDataPath, PerfectMachineList=[])

        # Analyze pre processed data and generate cell-based report
        print("Start Analyse By Panel Not Split", time.time())
        EM_Algorithm2.micro_crack_esimator(ProcessedDataPathByCellNotSplit, ReportPathByCellNotSplit)
        print("Finish", time.time())

        # Analyze pre processed data and generate panel-based report
        print("Start Analyse By Panel Not Split", time.time())
        EM_Algorithm2.micro_crack_esimator(ProcessedDataPathByPanelNotSplit, ReportPathByPanelNotSplit)
        print("Finish", time.time())

        # Linear Least Squares To Solve Weekly
        LinearLeastSquaresToSolveWeeklyYield.ComputeWeeklyYieldWithLeastSquare()

    # return HttpResponse('上传分析完毕')
    return HttpResponseRedirect(reverse('estimator:report-list'))

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
                    check_out_time_list = df['CHECK OUT TIME'].values.copy()
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

                        # Convert check_in_time and check_out_time into week
                        check_in_time = str(check_in_time_list[counter]).replace('/', '-')
                        check_out_time = str(check_out_time_list[counter]).replace('/', '-')

                        instance = Maintenance_History(
                            machine=str(machine_list[counter]),
                            check_in_time=check_in_time,
                            check_out_time=check_out_time,
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
                            outsourcing=str(outsourcing[counter]),
                            station_class=str(station_class[counter]),
                            station_name=str(station_name[counter]),
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
class ReportDownload(FormView):
    form_class = ReportForm
    template_name = 'estimator/report-download.html'
    success_url = reverse_lazy('estimator:report-download')

# END Report Views

# BEGIN Trend Views
class TrendView(View):
    def get(self, request):
        form = TrendForm()
        return render(request, 'estimator/trend.html', {'form': form})

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

        machine_yield_rate = Machine_Yield_Rate_History.objects\
            .values('period', 'yield_rate')\
            .filter(machine=machine, start_period__range=(start_date, end_date), end_period__range=(start_date, end_date), analyze_type=report_type)\
            .order_by('end_period')

        machine_maintenance = Maintenance_History.objects\
            .values('check_in_time')\
            .filter(machine=machine, check_in_time__range=(start_date, end_date), check_out_time__range=(start_date, end_date))\
            .order_by('check_in_time')

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
            'yield_rate': list(machine_yield_rate),
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
# END Trend Views

# END ProductionDataQuery Views
class ProductionDataQuery(View):
    def get(self, request):
        form = ProductionDataQueryForm()
        return render(request, 'estimator/production-data-query.html', {'form': form})

@csrf_exempt
def query_production_data(request):
    if request.is_ajax():
        # Retrieve user input from frontend
        input_type = request.GET.get('input_type', None)
        value = request.GET.get('value', None)

        # Perform query here...

# Create LOT and GBOM autocomplete here also...
