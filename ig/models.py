#-*- coding: utf-8 -*-
from django.db import models
from datetime import datetime

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

	def __unicode__(self):
		return (self.created_time.strftime("%Y-%m-%d %H:%M:%S : ")) + (u'%s posted a %s with %s' % (self.username, self.media_type, self.tagname))
