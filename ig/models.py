#-*- coding: utf-8 -*-
from django.db import models


class Post(models.Model):
	username = models.CharField(max_length=100)
	posted_date = models.DateTimeField(auto_now_add=True)
	instagram_id = models.IntegerField()
	post_url = models.URLField()
	media_type = models.CharField(max_length=20)
	media_url_lowres = models.URLField()
	media_url_stdres = models.URLField()

	def __unicode__(self):
		return u"Instagram: {0} post on {1} -> {2}".format(self.username).format(self.date).format(self.media_url_lowres)
