# Generated by Django 2.1.2 on 2018-12-03 20:05

from django.db import migrations, models
import django.db.models.deletion
import estimator.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bad_Phenomenon_By_Time',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lot_number', models.TextField(max_length=255, null=True)),
                ('check_in_time', models.TextField(max_length=255, null=True)),
                ('defect_category', models.TextField(max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': 'Bad Phenomena By Time',
                'ordering': ['check_in_time'],
                'verbose_name': 'Bad Phenomenon By Time',
            },
        ),
        migrations.CreateModel(
            name='Bad_Phenomenon_By_Warehouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lot_number', models.TextField(max_length=255, null=True)),
                ('check_in_time', models.TextField(max_length=255, null=True)),
                ('defect_category', models.TextField(max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': 'Bad Phenomena By Warehouse',
                'verbose_name': 'Bad Phenomenon By Warehouse',
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(max_length=5)),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('time_range', models.CharField(max_length=17, null=True)),
                ('file', models.FileField(upload_to=estimator.models.user_directory_path)),
                ('type', models.IntegerField(choices=[(0, 'Raw Production Data (by Check In Time)'), (1, 'Raw Production Data (by Warehouse Checking Date)'), (2, 'Machine Maintenance History'), (3, 'Machine Bad Phenomenon Data (by Check In Time)'), (4, 'Machine Bad Phenomenon Data (by Warehouse Checking Date)'), (5, 'GBOM Data')], default=0)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['last_modified'],
            },
        ),
        migrations.CreateModel(
            name='GBOM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gbom', models.TextField(max_length=255, null=True)),
                ('station', models.TextField(max_length=255, null=True)),
                ('station_number', models.TextField(max_length=255, null=True)),
                ('outsourcing', models.TextField(max_length=255, null=True)),
                ('station_class', models.CharField(max_length=255, null=True)),
                ('station_name', models.TextField(max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': 'GBOMs',
                'verbose_name': 'GBOM',
            },
        ),
        migrations.CreateModel(
            name='LOT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('LOT', models.CharField(max_length=50)),
                ('GBOM', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estimator.GBOM')),
            ],
            options={
                'verbose_name_plural': 'LOT',
                'verbose_name': 'LOT',
            },
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine', models.CharField(max_length=6)),
                ('type', models.CharField(max_length=10)),
                ('GBOM', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estimator.GBOM')),
                ('LOT', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estimator.LOT')),
            ],
        ),
        migrations.CreateModel(
            name='Maintenance_History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine', models.TextField(max_length=6)),
                ('check_in_time', models.DateTimeField()),
                ('employee_id', models.TextField(max_length=5)),
                ('operation_class', models.TextField(max_length=5)),
                ('major_code', models.TextField(max_length=15)),
                ('major_desc', models.TextField(max_length=255)),
                ('minor_code', models.TextField(max_length=15)),
                ('minor_desc', models.TextField(max_length=255)),
                ('description', models.TextField(max_length=255)),
                ('solution', models.TextField(max_length=255)),
                ('reason', models.TextField(max_length=255)),
                ('replace_parts', models.TextField(max_length=5)),
            ],
            options={
                'verbose_name_plural': 'Maintenance Histories',
                'ordering': ['check_in_time'],
                'verbose_name': 'Maintenance History',
            },
        ),
        migrations.CreateModel(
            name='Production_Data_By_Time',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_number', models.TextField(max_length=255, null=True)),
                ('check_in_time', models.DateTimeField(null=True)),
                ('gbom', models.TextField(max_length=255, null=True)),
                ('lot_number', models.TextField(max_length=255, null=True)),
                ('station_number', models.TextField(max_length=255, null=True)),
                ('station', models.TextField(max_length=255, null=True)),
                ('station_name', models.TextField(max_length=255, null=True)),
                ('machine_number', models.TextField(max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': 'Production Data By Time',
                'ordering': ['check_in_time'],
                'verbose_name': 'Production Data By Time',
            },
        ),
        migrations.CreateModel(
            name='Production_Data_By_Warehouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_number', models.TextField(max_length=255, null=True)),
                ('check_in_time', models.DateTimeField(null=True)),
                ('gbom', models.TextField(max_length=255, null=True)),
                ('lot_number', models.TextField(max_length=255, null=True)),
                ('station_number', models.TextField(max_length=255, null=True)),
                ('station', models.TextField(max_length=255, null=True)),
                ('station_name', models.TextField(max_length=255, null=True)),
                ('machine_number', models.TextField(max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': 'Production Data By Warehouse',
                'verbose_name': 'Production Data By Warehouse',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.PositiveSmallIntegerField()),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('machine', models.CharField(max_length=6)),
                ('yield_rate', models.FloatField()),
                ('bad_pieces_est', models.BigIntegerField()),
                ('is_panels', models.BooleanField(choices=[(0, 'Cell-based'), (1, 'Panel-based')], default=0)),
            ],
            options={
                'ordering': ['week'],
            },
        ),
    ]
