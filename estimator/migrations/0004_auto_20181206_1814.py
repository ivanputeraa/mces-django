# Generated by Django 2.1.2 on 2018-12-06 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estimator', '0003_auto_20181206_1813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenance_history',
            name='check_in_week',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]
