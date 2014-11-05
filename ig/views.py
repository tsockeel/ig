#-*- coding: utf-8 -*-
from django.views.decorators.http import require_http_methods
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from ig.models import Post
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.db.models import Q
import datetime
import json
import zmq

from instagram import client, subscriptions


CONFIG = {
        'client_id': 'fbdea8d4fb164caa98fb378f1ba1e9bf',
        'client_secret': 'bbe9f959a1ff4568b9369b76b8d6f133',
        'redirect_uri': 'http://66.228.61.74:8001/ig/oauth'
}

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)

def send_zmq_message(message):
	try:
        	socket.bind("tcp://66.228.61.74:%s" % port)
        except Exception, e:
        	print 'bind exception: %s'% e

	socket.send(message)

def recent_tag(tagname):
	if not tagname:
		print 'No tag name from update ! '
		return

	if not access_token:
		print 'Missing Access Token'
		return
	try:
		api = client.InstagramAPI(access_token=access_token)
		tag_search, next_tag = api.tag_search(q=tagname)
		recent_media, next = api.tag_recent_media(tag_name=tag_search[0].name, count=1)

		for media in recent_media:
#			print 'new media %s' % media.link
#			send_zmq_message(tagname + " " + media.get_standard_resolution_url())

			try:
				Post.objects.get(instagram_id=media.id)
				print "got existing post"
			except Post.DoesNotExist:
				Post.objects.create(username=media.user.username, instagram_id=media.id, post_url=media.link, media_type=media.type, tagname=tagname, caption_text=media.caption.text, media_url_thumbnail=media.get_thumbnail_url(), media_url_stdres=media.get_standard_resolution_url())
				print "created post in database"

	except Exception, e:
		print 'recent_tag exception: %s' % e



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
		print 'home exception: %s' %e
	return render_to_response('ig/content.html', locals(), RequestContext(request))


def oauth(request):
	code = request.GET.get("code")
	if not code:
		return 'Missing code'
	try:
		access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
		print "access token= " + access_token
		if not access_token:
			return 'Could not get access token'
		api = client.InstagramAPI(access_token=access_token)
		request.session['username'] = user_info['username']
		request.session['access_token'] = access_token

	except Exception, e:
		print 'oauth exception: %s' %e

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
                error = 'viewerupdate exception: %s' %e
		print error
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
		print 'recenttag exception: %s' %e
	return render_to_response('ig/content.html', locals(), RequestContext(request))


def subtag(request):
	if request.method == 'GET' and 'tagname' in request.GET and request.GET['tagname']:
		tagname = request.GET['tagname']
		print 'realtimetag %s' %tagname
		try:
			unauthenticated_api.create_subscription(object='tag', object_id=tagname, aspect='media', callback_url='http://66.228.61.74:8001/ig/postupdate/')
			print 'realtimetag subscription done'
		except Exception, e:
			print 'realtimetag exception: %s' % e
		return redirect('home')


def rmsubtag(request, id):
	try:
		unauthenticated_api.delete_subscriptions(id=id)
	except Exception, e:
		print 'realtimeremove exception: %s'% e
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
			print 'postupdate exception: %s' %e

	return HttpResponse('Parsed instagram')
