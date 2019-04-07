from django.conf.urls import url
from . import views

app_name = 'competition'

urlpatterns = [
    url(r'^event-create/$', views.event_create, name='event_create'),
    url(r'^event-detail/(?P<id>\d+)/(?P<competition_name>[-\w\ ]+)/$',
        views.detail_event, name='event_detail'),
    url(r'^list/$', views.event_list, name='list'),
    url(r'^event-sign-up/(?P<id>\d+)/$', views.sign_up, name='sign_up'),
    url(r'^event-resign/(?P<id>\d+)/$', views.resign, name='resign'),
    url(r'^event-edit/(?P<id>\d+)/(?P<competition_name>[-\w\ ]+)/$',
        views.event_edit, name='event_edit'),
]
