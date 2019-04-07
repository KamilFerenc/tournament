from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from .models import User
from django.contrib.auth.password_validation import validate_password
import datetime


class LoginForm(forms.Form):

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label='Email', widget=forms.EmailInput)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)
    location = forms.CharField(label='City', required=False)
    date_of_birth = forms.DateField(initial='01/30/2000',
                                    widget=DatePickerInput(format='%m/%d/%Y'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'date_of_birth', 'location', 'sport_club', 'is_competitor',
                  'is_organizer', 'photo')

    def clean(self):
        cd = super().clean()
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        elif cd['date_of_birth'] > datetime.date.today():
            raise forms.ValidationError("Seriously are you coming "
                                        "from the future?")
        validate_password(cd['password'])
        return cd


class UserEditForm(forms.ModelForm):

    date_of_birth = forms.DateField(widget=DatePickerInput(format='%m/%d/%Y'))

    def clean(self):
        cd = super().clean()
        if cd['date_of_birth'] > datetime.date.today():
            raise forms.ValidationError("Seriously are you coming "
                                        "from the future?")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'location',
                  'date_of_birth', 'sport_club', 'is_competitor',
                  'is_organizer', 'photo')
