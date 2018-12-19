from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone

import datetime

# Begin of PeiKai's code

# class HistoryMachineYieldRate(models.Model):
class Machine_Yield_Rate_History(models.Model):
    machine = models.TextField()
    period = models.TextField(null=True)
    start_period = models.DateField(default=timezone.now)
    end_period = models.DateField(default=timezone.now)
    yield_rate = models.FloatField()
    processed_pieces = models.TextField()
    analyze_type = models.TextField(default="Cell")

    class Meta:
        verbose_name = 'Machine Yield Rate History'
        verbose_name_plural = 'Machine Yield Rate Histories'
        ordering = ['yield_rate']

    def __str__(self):
        return str("(Week {0}) {1} , yield rate: {3}").format(self.period_in_week, self.machine, self.yield_rate)

class HistoryMachineUsage(models.Model):
      Lot = models.TextField()
      Period = models.TextField()
      Machine = models.TextField()

      class Meta:
          db_table = "HistoryMachineUsage"

class MachineUsedByLotInformation(models.Model):
    MaterialNumber = models.TextField()
    GBOM = models.TextField()
    Lot = models.CharField(max_length=255,db_index=True)
    FinishTime = models.TextField()
    TypeSettingNumber = models.TextField()
    Machine = models.CharField(max_length=255)
    CheckInTime = models.TextField()
    CheckOutTime = models.TextField()
    StationNumber = models.TextField()
    GoodPieces = models.TextField()
    BadPieces = models.TextField()
    FirstStation = models.TextField()
    CurrentTotalPieces = models.TextField()
    Period = models.CharField(max_length=255)

    class Meta:
        db_table = "MachineUsedByLotInformation"
        index_together = ["Period", "Machine"]
# End of PeiKai's code

class GBOM(models.Model):
    gbom = models.TextField(max_length=50, null=True)
    station = models.TextField(max_length=255, null=True)
    station_number = models.TextField(max_length=255, null=True)
    outsourcing = models.TextField(max_length=255, null=True)
    station_class = models.CharField(max_length=255, null=True)
    station_name = models.TextField(max_length=255, null=True)

    class Meta:
        verbose_name = 'GBOM'
        verbose_name_plural = 'GBOM'

    def __str__(self):
        return self.gbom

class LOT(models.Model):
    LOT = models.CharField(max_length=50)
    GBOM = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'LOT'
        verbose_name = 'LOT'

class Machine(models.Model):
    machine = models.CharField(max_length=6)
    type = models.CharField(max_length=10)
    GBOM = models.CharField(max_length=50)
    LOT = models.CharField(max_length=50)

    def __str__(self):
        return self.machine

# ALTER TABLE estimator_maintenance_history CONVERT TO CHARACTER SET big5 COLLATE big5_chinese_ci;
class Maintenance_History(models.Model):
    machine = models.TextField(max_length=6)
    check_in_time = models.DateTimeField(default=timezone.now)
    check_out_time = models.DateTimeField(default=timezone.now)
    employee_id = models.TextField(max_length=5)
    operation_class = models.TextField(max_length=5)
    major_code = models.TextField(max_length=15)
    major_desc = models.TextField(max_length=255)
    minor_code = models.TextField(max_length=15)
    minor_desc = models.TextField(max_length=255)
    description = models.TextField(max_length=255)
    solution = models.TextField(max_length=255)
    reason = models.TextField(max_length=255)
    replace_parts = models.TextField(max_length=5)

    class Meta:
        ordering = ['check_in_time']
        verbose_name = 'Maintenance History'
        verbose_name_plural = 'Maintenance Histories'

    def __str__(self):
        return self.machine

class Employee(models.Model):
    employee_id = models.CharField(max_length=5)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

# Uploaded file directory path
def user_directory_path(instance, filename):
    current_year = datetime.datetime.now().year
    start_period = instance.start_period.strftime('%Y%m%d').replace('-', '')
    end_period = instance.end_period.strftime('%Y%m%d').replace('-', '')

    if instance.type == 0:
        upload_path = 'uploads/Raw Production Data/By Check In Time/{0}/{1}_{2}.csv'.format(current_year, start_period, end_period)
    elif instance.type == 1:
        upload_path = 'uploads/Raw Production Data/By Warehouse Checking Date/{0}/{1}_{2}.csv'.format(current_year, start_period, end_period)
    elif instance.type == 2:
        upload_path = 'uploads/Machine Maintenance History/{0}/{1}_{2}.csv'.format(current_year, start_period, end_period)
    elif instance.type == 3:
        upload_path = 'uploads/Machine Bad Phenomenon Data/By Check In Time/{0}/{1}_{2}.csv'.format(current_year, start_period, end_period)
    elif instance.type == 4:
        upload_path = 'uploads/Machine Bad Phenomenon Data/By Warehouse Checking Date/{0}/{1}_{2}.csv'.format(current_year, start_period, end_period)
    elif instance.type == 5:
        upload_path = 'uploads/GBOM Data/{0}/{1}_{2}.csv'.format(current_year, start_period, end_period)
    else:
        upload_path = 'uploads/{0}/{1}_{2}.csv'.format(current_year, start_period, end_period)

    return upload_path

class File(models.Model):
    FILE_TYPE_CHOICES = (
        (0, 'Raw Production Data (by Check In Time)'),
        (1, 'Raw Production Data (by Warehouse Checking Date)'),
        (2, 'Machine Maintenance History'),
        (3, 'Machine Bad Phenomenon Data (by Check In Time)'),
        (4, 'Machine Bad Phenomenon Data (by Warehouse Checking Date)'),
        (5, 'GBOM Data'),
    )

    start_period = models.DateField(default=timezone.now)
    end_period = models.DateField(default=timezone.now)
    type = models.IntegerField(null=False, choices=FILE_TYPE_CHOICES, default=0)

    # Source : https://docs.djangoproject.com/en/2.1/ref/validators/#fileextensionvalidator
    file = models.FileField(upload_to=user_directory_path,
                            null=False,
                            validators=[FileExtensionValidator(["csv"])])
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_modified"]

    def __str__(self):
        return self.title

class Production_Data_By_Time(models.Model):
    part_number = models.TextField(max_length=255, null=True)
    check_in_time = models.DateTimeField(null=True)
    gbom = models.TextField(max_length=255, null=True)
    lot_number = models.TextField(max_length=255, null=True)
    station_number = models.TextField(max_length=255, null=True)
    station = models.TextField(max_length=255, null=True)
    station_name = models.TextField(max_length=255, null=True)
    machine_number = models.TextField(max_length=255, null=True)

    class Meta:
        ordering = ["check_in_time"]
        verbose_name = "Production Data By Time"
        verbose_name_plural = "Production Data By Time"

    def __str__(self):
        return self.part_number
#     Fill missing fields here...

class Production_Data_By_Warehouse(models.Model):
    part_number = models.TextField(max_length=255, null=True)
    check_in_time = models.DateTimeField(null=True)
    gbom = models.TextField(max_length=255, null=True)
    lot_number = models.TextField(max_length=255, null=True)
    station_number = models.TextField(max_length=255, null=True)
    station = models.TextField(max_length=255, null=True)
    station_name = models.TextField(max_length=255, null=True)
    machine_number = models.TextField(max_length=255, null=True)

    class Meta:
        verbose_name = "Production Data By Warehouse"
        verbose_name_plural = "Production Data By Warehouse"

    def __str__(self):
        return self.part_number

class Bad_Phenomenon_By_Time(models.Model):
    lot_number = models.TextField(max_length=255, null=True)
    check_in_time = models.TextField(max_length=255,null=True)
    defect_category = models.TextField(max_length=255, null=True)

    class Meta:
        ordering = ["check_in_time"]
        verbose_name = "Bad Phenomenon By Time"
        verbose_name_plural = "Bad Phenomena By Time"

    def __str__(self):
        return self.lot_name

class Bad_Phenomenon_By_Warehouse(models.Model):
    lot_number = models.TextField(max_length=255, null=True)
    check_in_time = models.TextField(max_length=255, null=True)
    defect_category = models.TextField(max_length=255, null=True)

    class Meta:
        verbose_name = "Bad Phenomenon By Warehouse"
        verbose_name_plural = "Bad Phenomena By Warehouse"

    def __str__(self):
        return self.lot_name