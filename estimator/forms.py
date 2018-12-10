from django import forms
from .models import File
from bootstrap_datepicker_plus import DatePickerInput

class FileForm(forms.ModelForm):
    file = forms.FileField(
        label='Select a File',
        help_text='Max. 15 MegaBytes'
    )

    time_range = forms.CharField(
        label='Time range (Optional)',
        help_text='Example : 20181201-20181208',
        required=False,
        max_length=17
    )

    class Meta:
        model = File
        fields = '__all__'

class TrendForm(forms.Form):

    REPORT_TYPE_CHOICES = (
        (0, 'Cell-based'),
        (1, 'Panel-based')
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
            "class": "form-control"
        }),
        max_length=6
    )

    is_panels = forms.ChoiceField(
        label='Report Type',
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
