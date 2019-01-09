from django import forms
from bootstrap_datepicker_plus import DatePickerInput


class TrendForm(forms.Form):

    REPORT_TYPE_CHOICES = (
        ('Cell', 'Cell-based'),
        ('Panel', 'Panel-based')
    )

    start_date = forms.DateField(
        widget=DatePickerInput(
            attrs={
                "autocomplete": "off"  # disable input history
            },
            options={
                "format": "YYYY-MM-DD",
                "minDate": "2018-01-01",  # PROJECT START DATE
                "useCurrent": False,
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
            }
        ),
        required=True
    )

    end_date = forms.DateField(
        widget=DatePickerInput(
            attrs={
                "autocomplete": "off"  # disable input history
            },
            options={
                "format": "YYYY-MM-DD",
                "useCurrent": False,
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
            }
        ),
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
