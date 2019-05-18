import datetime
import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.forms import forms as django_form
from django.test import TestCase
from mixer.backend.django import mixer
from competition import forms
from competition import models

pytestmark = pytest.mark.django_db


class SetupClass(TestCase):

    def setUp(self):
        self.organizer = mixer.blend('account.User', is_active=True,
                                     is_organizer=True)

        self.competition_rank = models.EventRank.objects.create(
            competition_rank='World Championship', cup='')

        self.discipline = models.EventDiscipline.objects.create(
            discipline='Ping Pong')
        self.form_data_valid = {
            'competition_name': 'Test Competition',
            'competition_rank': self.competition_rank.pk,
            'discipline': self.discipline.pk,
            'competition_date': self.future_date(15),
            'applications_deadline': self.future_date(10),
            'max_competitors': 32,
            'description': 'Lorem Ipsum is simply dummy text of the '
                           'printing and typesetting industry.',
            'country': 'Poland',
            'city': 'Kraków',
            'street': 'Aleja Mickiewicza',
            'number': 1,
            'poster': 'test.jpg',
        }

    # For generate proper date in the past (invalid form data)
    @staticmethod
    def past_date():
        return datetime.date.today() - datetime.timedelta(days=1)

    # For generate proper date in the future (form data)
    @staticmethod
    def future_date(days):
        return datetime.date.today() + datetime.timedelta(days=days)


class TestEventCreateForm(SetupClass):

    def test_form_valid_data(self):
        form = forms.EventCreateForm(data=self.form_data_valid)
        new_event = form.save(commit=False)
        new_event.organizer_id = self.organizer.pk
        new_event.save()
        check_event_in_db = \
            models.Event.objects.get(competition_name=
                                     self.form_data_valid['competition_name'])

        assert form.is_valid() is True
        assert check_event_in_db.pk == 1

    def test_form_invalid_competition_date(self):
        form_invalid_competition_date = {
            **self.form_data_valid,
            'competition_date': super().past_date()
        }
        form = forms.EventCreateForm(data=form_invalid_competition_date)
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.organizer_id = self.organizer.pk
            new_event.save()
        expected_error = \
            "'Competition date' is incorrect. Date must  be in the future."

        assert expected_error in form.non_field_errors().as_text()
        assert form.is_valid() is False
        with self.assertRaises(django_form.ValidationError):
            form.clean()
        with self.assertRaises(ObjectDoesNotExist):
            models.Event.objects.get(competition_name=
                                     self.form_data_valid['competition_name'])

    def test_form_invalid_applications_deadline(self):
        form_invalid_applications_deadline = {
            **self.form_data_valid,
            'applications_deadline': super().past_date()
        }
        form = forms.EventCreateForm(data=form_invalid_applications_deadline)
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.organizer_id = self.organizer.pk
            new_event.save()
        expected_error = "'Applications deadline' date is incorrect. " \
                         "Date must be in the future"

        assert expected_error in form.non_field_errors().as_text()
        assert form.is_valid() is False
        with self.assertRaises(django_form.ValidationError):
            form.clean()
        with self.assertRaises(ObjectDoesNotExist):
            models.Event.objects.get(competition_name=
                                     self.form_data_valid['competition_name'])

    def test_create_event_no_user(self):
        form = forms.EventCreateForm(data=self.form_data_valid)
        new_event = form.save(commit=False)
        new_event.organizer_id = None
        assert form.is_valid() is True
        with self.assertRaises(IntegrityError):
            new_event.save()
