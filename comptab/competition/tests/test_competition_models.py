import pytest
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from competition import models

pytestmark = pytest.mark.django_db


class TestEventRank:

    def test_model(self):
        event_rank = mixer.blend('competition.EventRank', cup='test.jpg')
        assert event_rank.pk == 1
        mixer.cycle(4).blend('competition.EventRank', cup='')
        all_events_rank = models.EventRank.objects.all().count()
        # Should return 5: 1 (event_rank) + 4 (mixer.cycle(4))
        assert all_events_rank == 5

    def test___str__(self):
        event_rank = mixer.blend('competition.EventRank',
                                 competition_rank='World Championship',
                                 cup='test_rank.jpg')
        result = event_rank.__str__()
        assert result == 'World Championship'


class TestEventDiscipline:

    def test_model(self):
        discipline = mixer.blend('competition.EventDiscipline')
        assert discipline.pk == 1

    def test___str__(self):
        discipline = mixer.blend('competition.EventDiscipline',
                                 discipline='Ping Pong')
        result = discipline.__str__()
        assert result == 'Ping Pong'


class TestEvent(TestCase):

    def setUp(self):
        self.competition_rank = mixer.blend('competition.EventRank', cup='')
        self.competition_rank_2 = mixer.blend('competition.EventRank', cup='')
        self.competition_name = 'Test name'

    def test_model(self):
        event = mixer.blend('competition.Event', poster='',
                            competition_rank=self.competition_rank)
        assert event.pk == 1
        mixer.cycle(9).blend('competition.Event', poster='',
                                      competition_rank=self.competition_rank_2)
        all_events = models.Event.objects.all().count()
        # Should return 10: 1 (event) + 9 (mixer.cycle(9))
        assert all_events == 10

    def test___str__(self):
        event = mixer.blend('competition.Event',
                            competition_name=self.competition_name,
                            poster='', competition_rank=self.competition_rank)
        result = event.__str__()
        assert result == 'Competition {}.'.format(self.competition_name)

    def test_get_absolute_url(self):
        event = mixer.blend('competition.Event',
                            competition_name=self.competition_name,
                            poster='', competition_rank=self.competition_rank)
        result = event.get_absolute_url()
        expected_url = reverse('competition:event_detail',
                               args=[event.id, event.competition_name])
        assert result == expected_url
