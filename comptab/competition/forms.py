from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from .models import Event
import datetime


class EventCreateForm(forms.ModelForm):

    competition_name = forms.CharField(label='Event')
    competition_date = forms.DateField(
        widget=DatePickerInput(format='%m/%d/%Y'))
    applications_deadline = forms.DateField(
        widget=DatePickerInput(format='%m/%d/%Y'))

    class Meta:
        model = Event
        fields = ('competition_name', 'competition_rank', 'discipline',
                  'competition_date', 'applications_deadline',
                  'max_competitors', 'description', 'country', 'city',
                  'street', 'number', 'poster')

    field_order = ['competition_name', 'competition_rank', 'discipline',
                   'competition_date', 'applications_deadline', 'description',
                   'country', 'city', 'street', 'number', 'poster']

    def clean(self):
        cd = super().clean()
        if cd['competition_date'] < datetime.date.today():
            raise forms.ValidationError("'Competition date' is incorrect. "
                                        "Date must  be in the future.")
        elif cd['applications_deadline'] < datetime.date.today():
            raise forms.ValidationError("'Applications deadline' date is "
                                        "incorrect. Date must be in the future")
        return cd
