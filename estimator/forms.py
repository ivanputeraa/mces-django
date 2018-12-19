from django import forms
from .models import *
from bootstrap_datepicker_plus import DatePickerInput


class FileForm(forms.ModelForm):
    start_period = forms.DateField(
        widget=DatePickerInput(format='%Y-%m-%d'),
        required=True
    )

    end_period = forms.DateField(
        widget=DatePickerInput(format='%Y-%m-%d'),
        required=True
    )

    file = forms.FileField(
        label='Select a File',
        help_text='Max. 15 MegaBytes'
    )

    class Meta:
        model = File
        fields = '__all__'


class TrendForm(forms.Form):

    REPORT_TYPE_CHOICES = (
        ('Cell', 'Cell-based'),
        ('Panel', 'Panel-based')
    )

    start_date = forms.DateField(
        widget=DatePickerInput(format='%Y-%m-%d'),
        required=True
    )

    end_date = forms.DateField(
        widget=DatePickerInput(format='%Y-%m-%d'),
        required=True
    )

    machine = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "autocomplete": "off"  # disable input history
        }),
        max_length=6
    )

    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(),
        required=True
    )


class ProductionDataQueryForm(forms.Form):
    QUERY_TYPE_CHOICES = (
        (0, 'GBOM'),
        (1, 'LOT')
    )

    input_type = forms.ChoiceField(
        label='Query based on:',
        choices=QUERY_TYPE_CHOICES,
        widget=forms.Select(),
        required=True
    )

    value = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control"
        }),
        max_length=50,
    )


class ReportForm(forms.Form):

    period = forms.ChoiceField(
        label='Select report period:',
        choices=[],
        widget=forms.Select(),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['period'].choices = [(period, period) for period in Machine_Yield_Rate_History.objects
            .values_list('period', flat=True)
            .distinct()
            .order_by('-end_period')]
