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


