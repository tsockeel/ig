#-*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from ig import views

urlpatterns = patterns('ig.views',
	url(r'^$', views.home, name='home'),
	url(r'^oauth/$', views.oauth, name='oauth'),
	url(r'^tag/(?P<tagname>\w{0,50})/$', views.tag, name='tag'),
	url(r'^subtag/$', views.subtag, name='subtag'),
	url(r'^rmsubtag/(?P<id>[0-9]+)$', views.rmsubtag, name='rmsubtag'),
	url(r'^postupdate/', views.postupdate, name='postupdate'),
)