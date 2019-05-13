import pytest
from django.urls import reverse
from mixer.backend.django import mixer
pytestmark = pytest.mark.django_db


class TestUser:

    def test_model(self):
        user = mixer.blend('account.User')
        assert user.pk == 1, 'Should create a User instance'

    def test_username(self):
        user = mixer.blend('account.User', username='Kamil')
        assert user.username == 'Kamil', 'Should return username'

    def test___str__(self):
        user = mixer.blend('account.User', username='Kamil')
        result = user.__str__()
        assert result == 'Profile user Kamil.'

    def test_get_absolute_url(self):
        user = mixer.blend('account.User')
        result = user.get_absolute_url()
        url = reverse('account:user_detail', args=[user.username])
        assert result == url
