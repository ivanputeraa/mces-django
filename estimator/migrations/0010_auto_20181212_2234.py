# Generated by Django 2.1.2 on 2018-12-12 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estimator', '0009_auto_20181212_2208'),
    ]

    operations = [
        migrations.RenameField(
            model_name='machine_yield_rate_history',
            old_name='end_period',
            new_name='period',
        ),
        migrations.RemoveField(
            model_name='machine_yield_rate_history',
            name='start_period',
        ),
        migrations.AddField(
            model_name='machine_yield_rate_history',
            name='period_in_week',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]