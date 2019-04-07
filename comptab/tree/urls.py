from django.conf.urls import url
from . import views

app_name = 'tournament'

urlpatterns = [
    url(r'^tournament/(?P<id>\d+)/(?P<competition_name>[-\w\ ]+)/$',
        views.tournament, name="tournament"),
    url(r'^tournament/match/(?P<player1_id>\d+)-vs-(?P<player2_id>\d+)/-eventid-(?P<event_id>\d+)/$',
        views.play_match, name='match'),
    url(r'^play-set/(?P<match_id>\d+)/$', views.play_set, name='play_set'),
    url(r'^add-points/(?P<set_id>\d+)/(?P<player>\d+)/$',
        views.add_points, name='add_points'),

]
