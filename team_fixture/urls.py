from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<fixture_id>[0-9]+)/$', views.main, name='team_fixture'),
]