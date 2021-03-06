from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from instaq import views

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^livegallery/(?P<eventname>\w{0,50})/$', views.livegallery, name='livegallery'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^createevent/$', views.create_event, name='create_event'),
    url(r'^rmevent/(?P<eventid>[0-9]+)$', views.remove_event, name='remove_event'),
    url(r'^pauseevent/(?P<eventid>[0-9]+)$', views.pause_event, name='pause_event'),
    url(r'^resumeevent/(?P<eventid>[0-9]+)$', views.resume_event, name='resume_event'),
    url(r'^createtag/$', views.create_tag, name='create_tag'),
    url(r'^rmtag/(?P<tagid>[0-9]+)$', views.remove_tag, name='remove_tag'),
)

