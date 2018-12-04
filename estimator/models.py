from django.db import models
from django.core.validators import FileExtensionValidator

class GBOM(models.Model):
    gbom = models.TextField(max_length=255, null=True)
    station = models.TextField(max_length=255, null=True)
    station_number = models.TextField(max_length=255, null=True)
    outsourcing = models.TextField(max_length=255, null=True)
    station_class = models.CharField(max_length=255, null=True)
    station_name = models.TextField(max_length=255, null=True)

    class Meta:
        verbose_name = 'GBOM'
        verbose_name_plural = 'GBOMs'

    def __str__(self):
        return self.gbom

class LOT(models.Model):
    LOT = models.CharField(max_length=50)
    GBOM = models.ForeignKey(to=GBOM, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'LOT'
        verbose_name = 'LOT'

class Machine(models.Model):
    machine = models.CharField(max_length=6)
    type = models.CharField(max_length=10)
    GBOM = models.ForeignKey(to=GBOM, on_delete=models.CASCADE)
    LOT = models.ForeignKey(to=LOT, on_delete=models.CASCADE)

class Report(models.Model):
    REPORT_TYPE_CHOICES = (
        (0, 'Cell-based'),
        (1, 'Panel-based'),
    )

    week = models.PositiveSmallIntegerField(null=False)
    last_modified = models.DateTimeField(auto_now=True)
    machine = models.CharField(max_length=6, null=False)
    yield_rate = models.FloatField()
    bad_pieces_est = models.BigIntegerField()
    is_panels = models.BooleanField(choices=REPORT_TYPE_CHOICES, default=0)

    class Meta:
        ordering = ['week']

    def __str__(self):
        return "(Week {0}) {1}".format(self.week, self.machine)

class Maintenance_History(models.Model):
    machine = models.TextField(max_length=6)
    check_in_time = models.DateTimeField()
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
    if instance.type == 0:
        upload_path = 'uploads/Raw Production Data/By Check In Time/{0}.csv'.format(instance.title)
    elif instance.type == 1:
        upload_path = 'uploads/Raw Production Data/By Warehouse Checking Date/{0}.csv'.format(instance.title)
    elif instance.type == 2:
        upload_path = 'uploads/Machine Maintenance History/{0}.csv'.format(instance.title)
    elif instance.type == 3:
        upload_path = 'uploads/Machine Bad Phenomenon Data/By Check In Time/{0}.csv'.format(instance.title)
    elif instance.type == 4:
        upload_path = 'uploads/Machine Bad Phenomenon Data/By Warehouse Checking Date/{0}.csv'.format(instance.title)
    elif instance.type == 5:
        upload_path = 'uploads/GBOM Data/{0}.csv'.format(instance.title)
    else:
        upload_path = 'uploads/{0}.csv'.format(instance.title)

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

    title = models.CharField(max_length=255, null=False)
    time_range = models.CharField(max_length=17, null=True)

    # Source : https://docs.djangoproject.com/en/2.1/ref/validators/#fileextensionvalidator
    file = models.FileField(upload_to=user_directory_path,
                            null=False,
                            validators=[FileExtensionValidator(["csv"])])
    type = models.IntegerField(null=False, choices=FILE_TYPE_CHOICES, default=0)
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