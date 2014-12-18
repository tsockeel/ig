#-*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.utils.timezone import localtime

class Event(models.Model):
	name = models.CharField(max_length=50)
	owner = models.ForeignKey(User)
	created_time = models.DateTimeField(auto_now_add=True)
	start_time = models.DateTimeField()
	stop_time = models.DateTimeField()
	paused = models.BooleanField(default=False)

	def __str__(self):
		return self.name

	
class Tag(models.Model):
	name = models.CharField(max_length=50)
	event = models.ForeignKey(Event)

	def __str__(self):
                return self.name


class Post(models.Model):
	tag = models.ForeignKey(Tag)
	instagram_id = models.CharField(max_length=50)
	created_time = models.DateTimeField(auto_now_add=True)
	url = models.URLField()
	event = models.ForeignKey(Event)

	def __unicode__(self):
		return ((u' id=%s - at ' % self.instagram_id) + localtime(self.created_time).strftime("%Y-%m-%d %H:%M:%S"))
