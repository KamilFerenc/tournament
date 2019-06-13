import datetime
import math
import pytest
from django.contrib.auth.models import AnonymousUser
from django import forms as django_form
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from competition.tests.test_competition_forms import SetupClass
from account import models as user_models
from competition import models, views


pytestmark = pytest.mark.django_db


class SetupTestsViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_organizer = mixer.blend(
            'account.User', is_active=True,
            is_competitor=False, is_organizer=True)
        self.user_competitor = mixer.blend(
            'account.User', is_active=True,
            is_competitor=True, is_organizer=False)
        self.competition_rank = models.EventRank.objects.create(
            competition_rank='World Championship', cup='')
        self.discipline = models.EventDiscipline.objects.create(
            discipline='Ping Pong')
        self.form_data_valid = {
            'competition_name': 'Test Competition',
            'competition_rank': self.competition_rank.pk,
            'discipline': self.discipline.pk,
            'competition_date': SetupClass.future_date(15),
            'applications_deadline': SetupClass.future_date(10),
            'max_competitors': 32,
            'description': 'Lorem Ipsum is simply dummy text of the '
                           'printing and typesetting industry.',
            'country': 'Poland',
            'city': 'Kraków',
            'street': 'Aleja Mickiewicza',
            'number': 1,
            'poster': 'test.jpg',
        }


class TestEventCreate(SetupTestsViews):

    def test_create_event_anonymous(self):
        self.client.logout()
        resp = self.client.get(reverse('competition:event_create'))
        assert resp.status_code == 302
        assert reverse('login') in resp.url

    def test_create_event_user_not_organizer(self):
        self.client.force_login(self.user_competitor)
        resp = self.client.get(reverse('competition:event_create'))
        expected_response = \
            'Sorry, to create an event you need to be the organizer.'
        assert resp.status_code == 200
        assert resp.content.decode() == expected_response

    def test_create_event_user_organizer_get(self):
        self.client.force_login(self.user_organizer)
        resp = self.client.get(reverse('competition:event_create'))
        assert resp.status_code == 200
        self.assertTemplateUsed(resp, 'events/event/create.html')

    def test_create_event_user_organizer_post_invalid_data(self):
        form_data_invalid = {
            **self.form_data_valid,
            'competition_rank': None,  # should be CompetitionRank instance
            'city': '',
        }
        self.client.force_login(self.user_organizer)
        resp = self.client.post(
            reverse('competition:event_create'), data=form_data_invalid)
        incorrect_city_error = b'This field is required.'
        incorrect_competition_rank_error =  \
            b'Select a valid choice. ' \
            b'That choice is not one of the available choices.'
        assert resp.status_code == 200
        assert incorrect_city_error in resp.content
        assert incorrect_competition_rank_error in resp.content

    def test_create_event_user_organizer_post(self):
        self.client.force_login(self.user_organizer)
        resp = self.client.post(
            reverse('competition:event_create'), data=self.form_data_valid)
        new_event = models.Event.objects.get(
            competition_name=self.form_data_valid['competition_name'])
        assert resp.status_code == 302
        assert resp.url == new_event.get_absolute_url()
        assert resp.url == reverse(
            'competition:event_detail',
            args=[new_event.id, new_event.competition_name])
        expected_organizer = user_models.User.objects.get(
            pk=self.client.session['_auth_user_id'])
        assert new_event.organizer == expected_organizer


class TestEventDetail(TestCase):

    def setUp(self):
        self.event = mixer.blend('competition.Event')
        self.user = mixer.blend('account.User')

    def test_event_detail_anonymous(self):
        resp = self.client.get(reverse(
            'competition:event_detail',
            args=[self.event.pk, self.event.competition_name]))
        assert resp.status_code == 200
        expected_event = models.Event.objects.get(id=self.event.pk)
        assert expected_event == resp.context['event']
        self.assertTemplateUsed(resp, 'events/event/detail.html')

    def test_event_detail_logged_user(self):
        resp = self.client.get(reverse(
            'competition:event_detail',
            args=[self.event.pk, self.event.competition_name]))
        assert resp.status_code == 200
        expected_event = models.Event.objects.get(id=self.event.pk)
        assert expected_event == resp.context['event']
        self.assertTemplateUsed(resp, 'events/event/detail.html')

    def test_no_existing_event(self):
        # event doesn't exist in DB
        incorrect_id = 12123
        incorrect_competition_name = 'no_existing_event'
        resp = self.client.get(reverse(
            'competition:event_detail',
            args=[incorrect_id, incorrect_competition_name]))
        assert resp.status_code == 404


class TestEventsList(SetupClass):

    def test_event_list_anonymous(self):
        # Create 5 instance of Event
        events_amount = 5
        mixer.cycle(events_amount).blend('competition.Event')
        returned_event = []
        # Pagination - page = 1
        resp_page_1 = self.client.get(reverse('competition:list'), {'page': 1})
        events_page_1 = len(resp_page_1.context['events'].object_list)
        returned_event.extend(resp_page_1.context['events'].object_list)
        assert resp_page_1.status_code == 200
        # Default 3 events per page
        assert events_page_1 == 3

        # Pagination - page = 2
        resp_page_2 = self.client.get(reverse('competition:list'), {'page': 2})
        events_page_2 = len(resp_page_2.context['events'].object_list)
        returned_event.extend(resp_page_2.context['events'].object_list)
        assert resp_page_2.status_code == 200
        # events_page_2 = events_amount - events_page_1 (5 - 3)
        assert events_page_2 == 2

        # Pagination - page = 3, should return last existing page
        resp_page_3 = self.client.get(reverse('competition:list'), {'page': 99})
        assert resp_page_3.status_code == 200
        assert (resp_page_2.context['events'].object_list
                == resp_page_3.context['events'].object_list)

        # Compare all returned events
        assert events_amount == events_page_1 + events_page_2
        assert (sorted(models.Event.objects.all(), key=lambda x: x.id)
                == sorted(returned_event, key=lambda x: x.id))

    # Testing except block of code - EmptyPage
    def test_event_list_page_out_of_range(self):
        # Describes in views.event_list
        events_per_page = 3
        # Create 4 events
        event = mixer.blend('competition.Event',
                            competition_date='2020-02-15')
        mixer.blend('competition.Event', competition_date='2019-02-15')
        mixer.blend('competition.Event', competition_date='2018-02-15')
        mixer.blend('competition.Event', competition_date='2017-02-15')
        all_events = models.Event.objects.all().count()
        maximum_page = math.ceil(all_events / events_per_page)
        # Page out of range (except block - EmptyPage)
        maximum_page += 1
        resp = self.client.get(reverse('competition:list'),
                               {'page': maximum_page})
        assert resp.status_code == 200
        # Returned object_list should contain 1 event:
        # all_events(4) - events_per_page(3) = 1
        assert len(resp.context['events'].object_list) == 1
        # Last page should contain the event with the latest competition_date
        assert resp.context['events'].object_list[0] == event

    # Testing except block of code - PageNotAnInteger
    def test_event_list_page_not_integer(self):
        mixer.blend('competition.Event', competition_date='2020-02-15')
        resp = self.client.get(reverse('competition:list'))
        assert resp.status_code == 200
        # Returned object_list should contain 1 event:
        assert len(resp.context['events'].object_list) == 1


class TestEventEditView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_organizer = mixer.blend(
            'account.User', is_active=True,
            is_competitor=False, is_organizer=True)
        self.event = mixer.blend(
            'competition.Event', organizer_id=self.user_organizer.pk)
        self.edit_data = {
            'competition_name': 'Test Edit Competition',
            'competition_date': SetupClass.future_date(15),
            'applications_deadline': SetupClass.future_date(10),
            'max_competitors': 32
        }
        self.client.force_login(self.user_organizer)

    def test_edit_event_anonymous(self):
        req = RequestFactory().get(reverse(
            'competition:event_edit',
            args=[self.event.pk, self.event.competition_name]))
        req.user = AnonymousUser()
        resp = views.event_edit(req)
        assert resp.status_code == 302
        assert reverse('login') in resp.url

    def test_edit_event_get(self):
        resp = self.client.get(reverse(
            'competition:event_edit',
            args=[self.event.pk, self.event.competition_name]))
        assert resp.status_code == 200

    def test_edit_event_post_valid_data(self):
        # create proper set of data in order to edit event detail
        event_data = django_form.model_to_dict(self.event)
        event_edit_data = {**event_data}
        event_edit_data.update(self.edit_data)
        poster = event_edit_data.pop('poster')
        resp = self.client.post(
            reverse('competition:event_edit',
                    args=[self.event.pk, self.event.competition_name]),
            data=event_edit_data, files=poster)
        self.event.refresh_from_db()
        expected_message = '"Edit event has finished successfully.'
        event_attributes_after_edit = (
            self.event.competition_name,
            self.event.competition_date,
            self.event.applications_deadline,
            self.event.max_competitors
        )
        assert resp.status_code == 302
        assert reverse(
            'competition:event_detail',
            args=[self.event.pk, self.event.competition_name]) in resp.url
        assert tuple(self.edit_data.values()) == event_attributes_after_edit
        assert expected_message in self.client.cookies['messages'].value

    def test_user_not_organizer(self):
        # logged in user who don't organize the event
        user = mixer.blend('account.User')
        self.client.force_login(user=user)
        resp = self.client.get(reverse(
            'competition:event_edit',
            args=[self.event.pk, self.event.competition_name]))
        expected_message = "You don't have permission for editing this event."
        assert resp.status_code == 302
        assert reverse('competition:event_detail',
                       args=[self.event.pk, self.event.competition_name]) in resp.url
        assert expected_message in self.client.cookies['messages'].value


class TestSignupView(TestCase):

    def setUp(self):
        self.client = Client()
        self.event = mixer.blend(
            'competition.Event',
            competition_date=SetupClass.future_date(30),
            applications_deadline=SetupClass.future_date(10),
            max_competitors=8,
        )
        self.user = mixer.blend('account.User',
                                is_active=True, is_competitor=True)

    def test_signup_view_user_anonymous(self):
        req = RequestFactory().get(reverse('competition:sign_up',
                                           args=[self.event.pk]))
        req.user = AnonymousUser()
        resp = views.sign_up(req)
        assert resp.status_code == 302
        assert reverse('login') in resp.url

    def test_signup_view_user_competitor_success(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('competition:sign_up',
                                       args=[self.event.pk]))
        all_competitors = self.event.competitors.all()
        expected_message = 'You sign up correctly.'
        assert self.user in all_competitors
        assert resp.status_code == 302
        assert reverse(
            'competition:event_detail',
            args=[self.event.pk, self.event.competition_name]) in resp.url
        assert expected_message in self.client.cookies['messages'].value

    def test_signup_view_user_competitor_not_success(self):
        self.users = mixer.cycle(10).blend(
            'account.User', is_active=True, is_competitor=True, photo='')
        # add competitors for the event
        self.event.competitors.add(*self.users[:8])
        # sing up competitors is equal event max competitors, requested user
        # cannot sign up successfully (max_competitors=8)
        self.client.force_login(self.user)
        resp = self.client.get(reverse('competition:sign_up',
                                       args=[self.event.pk]))
        all_competitors = self.event.competitors.all()
        expected_message = \
            'Sorry, registration is closed. Maximum numbers ' \
            'of competitors has been reached. You cannot sign up.'
        assert self.user not in all_competitors
        assert resp.status_code == 302
        assert reverse(
            'competition:event_detail',
            args=[self.event.pk, self.event.competition_name]) in resp.url
        assert expected_message in self.client.cookies['messages'].value

    def test_signup_view_applications_deadline_passed(self):
        # create event where applications_deadline has passed,
        # user cannot sign up successfully
        passed_applications_deadline = \
            datetime.date.today() - datetime.timedelta(days=5)
        event = mixer.blend('competition.Event',
                            competition_date=SetupClass.future_date(30),
                            applications_deadline=passed_applications_deadline)
        self.client.force_login(self.user)
        resp = self.client.get(reverse('competition:sign_up',
                                       args=[event.pk]))
        all_competitors = event.competitors.all()
        expected_message = 'Sorry, the deadline for registration has ' \
                           'expired. You cannot sign up.'
        assert self.user not in all_competitors
        assert resp.status_code == 302
        assert reverse('competition:event_detail',
                       args=[event.pk, event.competition_name]) in resp.url
        assert expected_message in self.client.cookies['messages'].value

    def test_signup_view_user_not_competitor(self):
        # user cannot sign up because isn't competitor (profile information)
        user = mixer.blend('account.User', is_competitor=False)
        self.client.force_login(user)
        resp = self.client.get(reverse('competition:sign_up',
                                       args=[self.event.pk]))
        all_competitors = self.event.competitors.all()
        expected_message = \
            "Sorry, you aren't competitor. " \
            "If you want to sign up for the competition edit the profile."
        assert user not in all_competitors
        assert resp.status_code == 302
        assert reverse(
            'competition:event_detail',
            args=[self.event.pk, self.event.competition_name]) in resp.url
        assert expected_message in self.client.cookies['messages'].value


class TestResignView(TestCase):

    def setUp(self):
        self.client = Client()
        self.event = mixer.blend('competition.Event')
        self.user = mixer.blend('account.User')
        self.event.competitors.add(self.user)

    def test_resign(self):
        self.client.force_login(self.user)
        # user should be in event.competitors (before calling resign view)
        assert self.user in self.event.competitors.all()
        resp = self.client.get(reverse('competition:resign',
                                       args=[self.event.id]))
        expected_message = 'You resign from competition.'
        assert resp.status_code == 302
        assert reverse(
            'competition:event_detail',
            args=[self.event.pk, self.event.competition_name]) in resp.url
        assert expected_message in self.client.cookies['messages'].value
        # user shouldn't be in event.competitors (after calling resign view)
        assert self.user not in self.event.competitors.all()

    def test_resign_user_not_signed_up(self):
        user_1 = mixer.blend('account.User', is_competitor=True)
        self.client.force_login(user_1)
        # user_1 shouldn't be in event.competitors
        assert user_1 not in self.event.competitors.all()
        resp = self.client.get(reverse('competition:resign',
                                       args=[self.event.id]))
        assert resp.status_code == 302
        assert reverse(
            'competition:event_detail',
            args=[self.event.pk, self.event.competition_name]) in resp.url
        assert user_1 not in self.event.competitors.all()
