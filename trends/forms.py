from django import forms
from bootstrap_datepicker_plus import DatePickerInput

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
