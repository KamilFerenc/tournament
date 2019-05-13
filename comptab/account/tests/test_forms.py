import datetime
import pytest
from django import forms as django_form
from django.test import TestCase
from account import forms
from account import models
pytestmark = pytest.mark.django_db


class TestUserRegistrationForm(TestCase):

    # Test form validation and overwrite method clean()

    form_data_valid = {'username': 'username', 'first_name': 'Jan',
                       'last_name': 'Kowalski',
                       'email': 'testform@test.com',
                       'date_of_birth': '01/28/1990', 'location': 'Krakow',
                       'sport_club': 'Klub', 'is_competitor': False,
                       'is_organizer': True, 'photo': '',
                       'password': 'abecadlo', 'password2': 'abecadlo'}

    @staticmethod
    def future_date():
        return datetime.date.today() + datetime.timedelta(days=10)

    def setUp(self):
        self.username = 'kamyk'
        self.email = 'test@test.com'
        self.password = 'test'
        self.test_user = models.User.objects.create_user(self.username,
                                                         self.email,
                                                         self.password)

    def test_form_valid_data(self):
        form = forms.UserRegistrationForm(data=self.form_data_valid)
        assert form.is_valid() is True, 'Should return True - form is valid.'

    def test_form_invalid_empty_username(self):
        form_data_invalid_username = {
            **self.form_data_valid,
            'username': '',
        }
        form = forms.UserRegistrationForm(data=form_data_invalid_username)
        expected_error = 'This field is required.'
        assert expected_error in form.errors['username']
        assert form.is_valid() is False, \
            'Should return False - username field (required) is empty'

    def test_username_already_exist(self):
        form_data_invalid_username = {
            **self.form_data_valid,
            'username': self.username,
        }
        form = forms.UserRegistrationForm(data=form_data_invalid_username)
        expected_error = 'A user with that username already exists.'
        assert expected_error in form.errors['username']
        assert form.is_valid() is False, \
            'Should return False - username already exist'

    def test_form_invalid_email(self):
        form_data_invalid_email = {
            **self.form_data_valid,
            'email': 'invalid#email.com',
        }
        form = forms.UserRegistrationForm(data=form_data_invalid_email)
        expected_error = 'Enter a valid email address.'
        assert form.is_valid() is False, \
            'Should return False - email field (required) is invalid'
        assert expected_error in form.errors['email']

    def test_form_invalid_different_password(self):
        form_data_invalid_different_password = {
            **self.form_data_valid,
            'password': 'abecadlo',
            'password2': 'abecadlo2',
        }
        form = forms.UserRegistrationForm(data=
                                          form_data_invalid_different_password)
        expected_error = "Passwords don't match."
        assert form.is_valid() is False, \
            'Should return False - password != password2'
        assert expected_error in form.non_field_errors().as_text()
        with self.assertRaises(django_form.ValidationError):
            form.clean()

    def test_form_invalid_password_too_short(self):
        form_data_invalid_password_too_short = {
            **self.form_data_valid,
            'password': '12ab',
            'password2': '12ab',
        }
        form = forms.UserRegistrationForm(data=
                                          form_data_invalid_password_too_short)
        assert form.is_valid() is False, \
            'Should return False - password to short'
        with self.assertRaises(django_form.ValidationError):
            form.clean()

    def test_form_invalid_date_of_birth(self):
        form_data_invalid_date_of_birth = {
            **self.form_data_valid,
            'date_of_birth': self.future_date(),
        }
        form = forms.UserRegistrationForm(data=
                                          form_data_invalid_date_of_birth)
        expected_error = 'Seriously are you coming from the future?'
        assert form.is_valid() is False, \
            'Should return False - date_of_birth from future'
        assert expected_error in form.non_field_errors()
        with self.assertRaises(django_form.ValidationError):
            form.clean()


class TestUserEditForm(TestCase):

    edit_data = {'first_name': 'Tomasz', 'last_name': 'Nowak',
                 'email': 'invalid@email.com', 'date_of_birth': '03/02/2000',
                 'location': 'Krakow', 'sport_club': 'Sport Klub',
                 'is_competitor': False, 'is_organizer': True,
                 'photo': 'sample.img'}

    def test_edit_form_valid_data(self):
        edit_form = forms.UserEditForm(data=self.edit_data)
        assert edit_form.is_valid() is True, \
            'Should return True - edit form valid'

    def test_edit_form_invalid_date_of_birth(self):
        edit_data_invalid_date_of_birth = {
            **self.edit_data,
            'date_of_birth': TestUserRegistrationForm.future_date(),
        }
        edit_form = forms.UserEditForm(data=edit_data_invalid_date_of_birth)

        expected_error = 'Seriously are you coming from the future?'
        assert edit_form.is_valid() is False, \
            'Should return False - date_of_birth from future'
        assert expected_error in edit_form.non_field_errors()
        with self.assertRaises(django_form.ValidationError):
            edit_form.clean()
