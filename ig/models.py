#-*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class Event(models.Model):
	name = models.CharField(max_length=50)
	owner = models.ForeignKey(User)
	created_time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name
	
class Tag(models.Model):
	name = models.CharField(max_length=50)
	event = models.ForeignKey(Event)

	def __str__(self):
                return self.name

class Recording(models.Model):
        tag = models.ForeignKey(Tag)


class Post(models.Model):
	username = models.CharField(max_length=100)
	tagname = models.CharField(max_length=50)
	caption_text = models.CharField(max_length=2200)
	instagram_id = models.CharField(max_length=50)
	created_time = models.DateTimeField(auto_now_add=True)
	post_url = models.URLField()
	media_type = models.CharField(max_length=20)
	media_url_thumbnail = models.URLField()
	media_url_stdres = models.URLField()
	event = models.ForeignKey(Event)

	def __unicode__(self):
		return (self.created_time.strftime("%Y-%m-%d %H:%M:%S : ")) + (u'%s posted a %s with %s' % (self.username, self.media_type, self.tagname))
