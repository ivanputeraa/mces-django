from django import forms
from estimator.models import Machine_Yield_Rate_History

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