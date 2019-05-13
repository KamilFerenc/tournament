import pytest
import copy
from django import forms as django_form
from django.contrib.auth import get_user_model, views as auth_views
from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase, Client
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from mixer.backend.django import mixer
from account import forms
from account import models
from account import tokens
from account import views

pytestmark = pytest.mark.django_db


class TestHomeView:

    def test_home_anonymous(self):
        req = RequestFactory().get(reverse('login'))
        resp = auth_views.LoginView.as_view()(req)
        assert resp.status_code == 200


class TestDashboard:

    def test_status_code_logged_in(self):
        user = mixer.blend('account.User')
        req = RequestFactory().get(reverse('account:dashboard'))
        req.user = user
        resp = views.dashboard(req)
        assert resp.status_code == 200

    def test_status_code_anonymous(self):
        req = RequestFactory().get(reverse('account:dashboard'))
        req.user = AnonymousUser()
        resp = views.dashboard(req)
        assert reverse('login') in resp.url
        assert resp.status_code == 302


class TestRegisterUser(TestCase):

    form_data = {
        'username': 'ferene', 'first_name': 'kamil',
        'last_name': 'ferenc', 'email': 'kamilferenc91@gmail.com',
        'date_of_birth': '05/28/1991', 'location': 'Krakow',
        'sport_club': 'KS Korona', 'is_competitor': False,
        'is_organizer': True, 'photo': '',
        'password': 'abecadlo', 'password2': 'abecadlo'
    }

    def test_register_get_method(self):
        req = RequestFactory().get(reverse('account:register'))
        resp = views.register(req)
        assert resp.status_code == 200

    def test_register_post_method_valid(self):
        req = RequestFactory().post(reverse('account:register'),
                                    data=self.form_data)
        resp = views.register(req)
        user = get_user_model().objects.get(username=self.form_data['username'])
        assert resp.content == b'Please check your email to ' \
                               b'complete the registration.'
        assert(user.is_active is False)
        assert resp.status_code == 200

    def test_register_post_method_invalid_data(self):
        self.form_data_invalid = copy.copy(self.form_data)
        self.form_data_invalid['username'] = ''
        response = self.client.post(reverse('account:register'),
                                    data=self.form_data_invalid)
        assert b'This field is required.' in response.content
        assert response.status_code == 200


class TestActivateUser(TestCase):

    def setUp(self):
        self.registered_user = mixer.blend('account.User', is_active=False)
        self.token = \
            tokens.account_activation_token.make_token(self.registered_user)
        self.uidb64 = urlsafe_base64_encode(
            force_bytes(self.registered_user.pk)).decode()

    def test_activate(self):
        resp = self.client.get(reverse('account:activate', args=(self.uidb64,
                                                                 self.token)))
        new_user = models.User.objects.get(
            pk=self.client.session.get('_auth_user_id'))
        assert resp.status_code == 302
        assert reverse('account:dashboard') in resp.url
        assert new_user.is_active

    def test_activate_invalid_uidb(self):
        wrong_uidb64 = 'wrong_value'
        resp = self.client.get(reverse('account:activate',  args=(wrong_uidb64,
                                                                  self.token)))
        assert b'Activation link is invalid.' in resp.content
        assert resp.status_code == 200

    def test_activate_invalid_token(self):
        token = 'wrong-value'
        resp = self.client.get(reverse('account:activate',  args=(self.uidb64,
                                                                  token)))
        assert b'Activation link is invalid.' in resp.content
        assert resp.status_code == 200


class TestLoginView(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = 'kamyk'
        self.email = 'test@test.com'
        self.password = 'test'
        self.test_user = models.User.objects.create_user(self.username,
                                                         self.email,
                                                         self.password)

    def test_login_redirect(self):
        resp = self.client.post(reverse('login'), {'username': self.username,
                                                   'password': self.password})
        assert reverse('account:dashboard') in resp.url
        assert resp.status_code == 302


class TestEditAccountView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = mixer.blend('account.User')
        self.user_data = django_form.model_to_dict(self.user)
        self.form_edit_data = {'first_name': 'kamil', 'last_name': 'ferenc',
                               'location': 'Krakow'}
        self.client.force_login(self.user)

    def test_user_edit_get_method(self):
        response = self.client.get(reverse('account:edit'))
        assert response.status_code == 200

    def test_user_edit_post_method_valid_data(self):
        self.user = \
            models.User.objects.get(pk=self.client.session['_auth_user_id'])
        self.user_data.update(self.form_edit_data)
        response = self.client.post(reverse('account:edit'),
                                    data=self.user_data)
        self.user.refresh_from_db()
        self.data_after_edit = (self.user.first_name, self.user.last_name,
                                self.user.location)
        assert self.data_after_edit == (tuple(self.form_edit_data.values()))
        assert response.status_code == 302
        assert reverse('account:dashboard') in response.url

    def test_user_edit_post_method_invalid_data(self):
        self.form_edit_invalid_data = copy.copy(self.form_edit_data)
        self.form_edit_invalid_data['date_of_birth'] = '05/28/2020'
        self.user_data.update(self.form_edit_invalid_data)
        edit_form = forms.UserEditForm(data=self.user_data)
        edit_form.is_valid()
        expected_error = 'Seriously are you coming from the future?'
        response = self.client.post(reverse('account:edit'),
                                    data=self.user_data)
        assert response.status_code == 200
        assert expected_error in edit_form.errors.as_text()
        with self.assertRaises(django_form.ValidationError):
            edit_form.clean()


class DataSetTestView(TestCase):

    # data set for TestCompetitorsListView and TestUserDetailView
    def setUp(self):
        self.client = Client()
        self.logged_user = mixer.blend('account.User', is_competitor=True)
        self.user_1 = mixer.blend('account.User', is_competitor=True)
        self.user_2 = mixer.blend('account.User', is_competitor=True)
        self.user_3 = mixer.blend('account.User', is_active=False)
        self.user_4 = mixer.blend('account.User', is_active=False)
        self.user_5 = mixer.blend('account.User', is_active=False,
                                  is_competitor=True)
        self.user_6 = mixer.blend('account.User', is_competitor=False)
        self.user_7 = mixer.blend('account.User', is_competitor=True)
        self.user_8 = mixer.blend('account.User', is_organizer=True)
        self.user_9 = mixer.blend('account.User', is_active=False,
                                  is_competitor=True)
        self.user_10 = mixer.blend('account.User', is_competitor=True)


class TestCompetitorsListView(DataSetTestView):

    def test_competitor_list_anonymous(self):
        resp = self.client.get(reverse('account:user_list'))
        assert resp.status_code == 302
        assert reverse('login') in resp.url

    def test_competitor_list(self):
        self.client.force_login(user=self.logged_user)
        resp = self.client.get(reverse('account:user_list'))

        expected_competitors = \
            models.User.objects.filter(is_competitor=True, is_active=True)
        expected_competitors = \
            expected_competitors.exclude(username=self.logged_user.username)
        competitors = resp.context['users']

        assert len(expected_competitors.difference(competitors)) == 0
        assert resp.status_code == 200
        self.assertTemplateUsed(resp, 'account/user/list.html')


class TestUserDetailView(DataSetTestView):

    def test_user_detail_anonymous(self):
        resp = self.client.get(reverse('account:user_list'))
        assert resp.status_code == 302
        assert reverse('login') in resp.url

    def test_existing_user(self):
        self.client.force_login(user=self.logged_user)
        resp = self.client.get(reverse('account:user_detail',
                                       args=(self.user_1.username, )))
        user = resp.context['user']
        assert self.user_1 == user
        assert resp.status_code == 200

    def test_no_existing_user(self):
        self.client.force_login(self.logged_user)
        # self.user_3 is not active
        resp = self.client.get(reverse('account:user_detail',
                                       args=(self.user_3.username, )))

        assert resp.status_code == 404, \
            'Should return status code 404, user is not active'
