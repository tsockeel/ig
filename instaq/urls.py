from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from instaq import views

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^createevent/$', views.create_event, name='create_event'),
)
