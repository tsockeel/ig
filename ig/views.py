#-*- coding: utf-8 -*-
from django.views.decorators.http import require_http_methods
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.db.models import Q
import datetime
from ig.models import Event, Tag, Post
from django.utils import timezone
import json
from django.conf import settings
import redis

import logging
logger = logging.getLogger('djangologger')


from instagram import client, subscriptions


CONFIG = {
        'client_id': 'fbdea8d4fb164caa98fb378f1ba1e9bf',
        'client_secret': 'bbe9f959a1ff4568b9369b76b8d6f133',
        'redirect_uri': 'http://66.228.61.74:8001/ig/oauth'
}

redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)



def recent_tag(tagname):
	if not tagname:
		logger.error('empty tagname on update from instagram')
		return

	if not access_token:
		logger.error('Missing Access Token')
		return
	try:
		activeTags = Tag.objects.filter(name=tagname)
		# database processing
		now = timezone.now()
		activeEvent1 = Event.objects.filter(stop_time__gt=now) #.filter(start_time__lt=now).filter(tag__name__contains=tagname)
		activeEvent2 = activeEvent1.filter(start_time__lt=now)#.filter(tag__name__contains=tagname)
		activeEvent3= activeEvent2.filter(tag__name__contains=tagname)
		activeEvents= activeEvent3.filter(paused=False)

		#instagram requests
		api = client.InstagramAPI(access_token=access_token)
		tag_search, next_tag = api.tag_search(q=tagname)
		recent_media, next = api.tag_recent_media(tag_name=tag_search[0].name, count=1)

		for media in recent_media:
			for activeEvent in activeEvents:
				try:
					Post.objects.get(instagram_id=media.id)
					logger.debug('got existing post - already tagged %s' % media.id)
				except Post.DoesNotExist:
					activeTag = activeTags.get(event = activeEvent.pk)
	                                url = "https://api.instagram.com/v1/media/" + media.id + "?client_id=" + CONFIG["client_id"]
					# saving in the database
					Post.objects.create(event=activeEvent, instagram_id=media.id, url=media.link, tag=activeTag)
					# sending notification
        	                        redis_server.publish("message", json.dumps( { 'url': url, 'eventname':activeEvent.name, 'tag':activeTag.name}))
					logger.debug('sending message %s' % url)

	except Exception, e:
		logger.error('caught exception: %s' % e)


def parse_instagram_update(update):
	tagName = update['object_id']
	recent_tag(tagName)


reactor = subscriptions.SubscriptionsReactor()
reactor.register_callback(subscriptions.SubscriptionType.TAG, parse_instagram_update)

unauthenticated_api = client.InstagramAPI(**CONFIG)
access_token = '1496477170.fbdea8d.efce8004aecd4ea4a0a0bb06d6ae3a0c'

def home(request):
	try:
		oauth_url = unauthenticated_api.get_authorize_url(scope=["basic"])
		subsc_list = unauthenticated_api.list_subscriptions()
	except Exception, e:
		logger.error('caught exception: %s' %e)
	return render_to_response('ig/content.html', locals(), RequestContext(request))


def oauth(request):
	code = request.GET.get("code")
	if not code:
		return 'Missing code'
	try:
		access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
		logger.info("access token= " + access_token)
		if not access_token:
			logger.error('Could not get access token')
			return 'Could not get access token'
		api = client.InstagramAPI(access_token=access_token)
		request.session['username'] = user_info['username']
		request.session['access_token'] = access_token

	except Exception, e:
		logger.error('caught exception: %s' %e)

	return redirect('home')


def viewer(request):
	posts = Post.objects.filter(tagname='instaq', media_type="image")
        return render_to_response('ig/viewer.html', locals(), RequestContext(request))


def viewerupdate(request):
	try:
		# get parameter to query the database
		entry_tagname = request.GET.get('tagname', '')
		if not entry_tagname:
			return HttpResponse("tagname is empty - nothing to return", content_type="text/plain")

		entry_start_date = request.GET.get('start_date', '2014-10-24T22:14:18.091Z')

		if not entry_start_date:
			entry_start_date = '2014-10-24T22:14:18.091Z'

		start_date = parse_datetime(entry_start_date) + datetime.timedelta(milliseconds=1)

		# Query the database - use reverse to have the latest post first
	        posts = Post.objects.filter(Q(tagname=entry_tagname) & Q(media_type="image") & Q(created_time__gt=start_date)).order_by('-created_time')
		
		# serialise the querydict object
		raw_data = serializers.serialize('python', posts)

		# build the JSON response - filter out useless information from database
		actual_data = {}
		if posts.count() > 0:
			actual_data['most_recent_post'] = posts[0].created_time
		actual_data['posts'] = [d['fields'] for d in raw_data]
		output = json.dumps(actual_data, cls=DjangoJSONEncoder)
		return HttpResponse(output, content_type='application/json')
	except Exception, e:
                error = 'caught viewerupdate exception: %s' %e
		logger.error(error)
		return HttpResponse(error, content_type="text/plain")
	# Less powerfull
	#return JsonResponse(list(posts), safe=False) 


def tag(request, tagname):
	media_content = ""
	if not tagname:
		return 'No tag name'
	try:
		api = client.InstagramAPI(access_token=access_token)
		tag_search, next_tag = api.tag_search(q=tagname)
		recent_media, next = api.tag_recent_media(tag_name=tag_search[0].name, count=20)

		photos = []
		for media in recent_media:
			photos.append('<div style="float:left;"> <a href=%s title=%s target="_blank">' % (media.link, "media.caption.text"))
			if(media.type == 'video'):
				photos.append('<video controls width height="150"><source type="video/mp4" src="%s"/></video>' % (media.get_standard_resolution_url()))
			else:
				photos.append('<img src="%s" alt="%s"/>' % (media.get_low_resolution_url(), "media.caption.text"))
			photos.append("</a><br/> </div>")
		media_content += ''.join(photos)
	except Exception, e:
		logger.error('caught exception: %s' %e)
	return render_to_response('ig/content.html', locals(), RequestContext(request))


def subscribeNewTag(tagToSubscribe):
	unauthenticated_api.create_subscription(object='tag', object_id=tagToSubscribe, aspect='media', callback_url='http://66.228.61.74:8001/ig/postupdate/')
	logger.info('API instagram: create tag subscription done for %s' %tagToSubscribe)

def getTagSubscription(tagname):
	subscriptions = unauthenticated_api.list_subscriptions()
	for subscription in subscriptions["data"]:
                if tagname == subscription["object_id"]:
			return subscription
	return {}

def createTagSubscription(newTagName):
	if not getTagSubscription(newTagName):
		subscribeNewTag(newTagName)

def deleteTagSubscription(tagToDelete):
	subscription = getTagSubscription(tagToDelete)
	if subscription:
		unauthenticated_api.delete_subscriptions(id=subscription["id"])
		logger.info('API instagram: delete tag subscription done for %s' %tagToDelete)


def subtag(request):
	if request.method == 'GET' and 'tagname' in request.GET and request.GET['tagname']:
		tagname = request.GET['tagname']
		logger.info('realtimetag %s' %tagname)
		try:
			createTagSubscription(tagname)
		except Exception, e:
			logger.error('caught exception: %s' % e)
		return redirect('home')


def rmsubtag(request, id):
	try:
		unauthenticated_api.delete_subscriptions(id=id)
	except Exception, e:
		logger.error('caught exception: %s'% e)
	return redirect('home')


@csrf_exempt
def postupdate(request):
	if request.method == 'GET':
		challenge = request.GET.get('hub.challenge')
		if challenge:
			return HttpResponse(challenge)
	else:
		x_hub_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
		raw_response = request.body

		try:
			reactor.process(CONFIG['client_secret'], raw_response, x_hub_signature)
		except Exception, e:
			logger.error('caught exception: %s' %e)

	return HttpResponse('Parsed instagram')

