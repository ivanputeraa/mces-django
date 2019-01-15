from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from django_tables2 import RequestConfig
from django.http import JsonResponse

from .forms import *
from .models import *
from .tables import MachineTables

from shutil import copyfile
from estimator import DataPreprocess
from estimator import EM_Algorithm2
from estimator import LinearLeastSquaresToSolveWeeklyYield

import pandas as pd
import os
import time


# Begin of PeiKai's code
def analyze_data(request, pk): # Rename from UploadAndAnalyze
    if request.is_ajax() and request.method == 'POST':

        file = File.objects.values_list('file', flat=True).filter(pk=pk)
        file_path = os.path.join(settings.MEDIA_ROOT, file[0])

        # Read the prod data file
        DataFlow = pd.read_csv(file_path, encoding='big5', low_memory=False)

        # Check whether prod data is the correct one
        if '入庫日期' not in DataFlow.columns.values:
            response = JsonResponse({
                "success": False,
                "error": "production data is wrong"
            })
            response.status_code = 403
        else:  # 根据入库时间重命名
            FinishTimeList = DataFlow['入庫日期'].values.copy()
            FinishTimeList.sort()
            FinishTimeRange = FinishTimeList[0] + "_" + FinishTimeList[len(FinishTimeList) - 1]
            FinishTimeRange = FinishTimeRange.replace("/", "_")

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

            response = JsonResponse({
                "success": True,
                "message": "Analyze done"
            })
            response.status_code = 200
        return response


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
    #paginate_by = 10
    template_name_suffix = '-list'
    file_list = File.objects.all().order_by('-last_modified')

    #def listing(request):

    #paginator = Paginator(file_list)

    #page = request.GET.get('page')
    #page_obj = paginator.get_page(page)
    #return render(request, 'estimator/file-list.html', {'file_list': page_obj})


@login_required
def file_create(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_type = form.cleaned_data['type']
            instances = []
            df = pd.read_csv(file, encoding='big5', header=0)

            # ALTER TABLE estimator_production_data_by_time CONVERT TO CHARACTER SET big5 COLLATE big5_chinese_ci;
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
                    # Delete previous maintenance history data
                    Maintenance_History.objects.all().delete()
                    File.objects.filter(type=2).delete()

                    machine_list = df['設備代碼'].values.copy()
                    serial_number_list = df['流水號'].values.copy()
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
                        instance = Maintenance_History(
                            machine=str(machine_list[counter]),
                            serial_number=str(serial_number_list[counter]),
                            check_in_time=str(check_in_time_list[counter]).replace('/', '-'),
                            check_out_time=str(check_out_time_list[counter]).replace('/', '-'),
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
    else:  # request.method == 'GET':
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

    def post(self, request, *args, **kwargs):
        file_id = self.kwargs.get('pk')
        file = File.objects.values_list('file', flat=True).filter(id=file_id)
        file_path = os.path.join(settings.MEDIA_ROOT + file[0])

        # Remove the actual file from server
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("The file does not exist")

        # Remove object from db
        get_object_or_404(File, pk=file_id).delete()

        return HttpResponseRedirect(reverse('estimator:file-list'))
# END File Upload Views


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

    table = MachineTables(Machine.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'tutorial/production-data-query.html', {'table': table})


    #istekler = Machine.objects.all()
    #return render(request, 'estimator/production-data-query.html', locals())

    # Perform query here...
# Create LOT and GBOM autocomplete here also...
