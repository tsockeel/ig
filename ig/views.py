#-*- coding: utf-8 -*-
from django.views.decorators.http import require_http_methods
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse


from instagram import client, subscriptions


CONFIG = {
	'client_id': '50b1709ec93a43659184b33f2027a781',
	'client_secret': 'df0aa23aca584a4dbfda8991b74a41e7',
	'redirect_uri': 'http://tsockeel.herokuapp.com/ig/oauth'
}

unauthenticated_api = client.InstagramAPI(**CONFIG)
access_token = '15254776.50b1709.478c82a701094816a1794b666b6721c4'

def home(request):
	try:
		oauth_url = unauthenticated_api.get_authorize_url(scope=["basic"])
	except Exception, e:
		print 'home exception: %s' %e
	return render_to_response('ig/base.html', locals(), RequestContext(request))


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
		#request.session['username'] = user_info['username']
		#request.session['access_token'] = access_token

	except Exception, e:
		print 'oauth exception: %s' %e

	return redirect('home')


def tag(request, tagname):
	media_content = ""
	if not tagname:
		return 'No tag name'
	try:
		api = client.InstagramAPI(access_token=access_token)
		tag_search, next_tag = api.tag_search(q=tagname)
		recent_media, next = api.tag_recent_media(tag_name=tag_search[0].name, count=2)

		photos = []
		for media in recent_media:
			photos.append('<div style="float:left;">')
			if(media.type == 'video'):
				photos.append('<video controls width height="150"><source type="video/mp4" src="%s"/></video>' % (media.get_standard_resolution_url()))
			else:
				photos.append('<img src="%s"/>' % (media.get_low_resolution_url()))
			photos.append("<br/> <a href='/media_like/%s'>Like</a>  <a href='/media_unlike/%s'>Un-Like</a>  LikesCount=%s</div>" % (media.id,media.id,media.like_count))
		media_content += ''.join(photos)
	except Exception, e:
		print 'recenttag exception: %s' %e
	return render_to_response('ig/content.html', locals(), RequestContext(request))


def subtag(request):
	if request.method == 'GET' and 'tagname' in request.GET and request.GET['tagname']:
		tagname = request.GET['tagname']
		print 'realtimetag %s' %tagname
		try:
			#unauthenticated_api.create_subscription(object='tag', object_id=tagname, aspect='media', callback_url='http://tsockeel.pythonanywhere.com/instagramprinter/callback/')
			unauthenticated_api.create_subscription(object='tag', object_id=tagname, aspect='media', callback_url='http://tsockeel.herokuapp.com/ig/postupdate/')
			print 'realtimetag subscription done'
		except Exception, e:
			print 'realtimetag exception: %s' % e
		return realtimelist(request)


def realtimelist(request):
	try:
		subsc_list = unauthenticated_api.list_subscriptions()
	except Exception, e:
		print 'realtimelist exception: %s'% e
	return render_to_response('ig/content.html', locals(), RequestContext(request))


def rmsubtag(request, id):
	try:
		unauthenticated_api.delete_subscriptions(id=id)
	except Exception, e:
		print 'realtimeremove exception: %s'% e
	return realtimelist(request)


def recent_tag(tagname):
	print 'recent-tag'
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
			print 'new media %s' % media.link
			#try:
			#	Post.objects.get(instagram_id=media.id)
			#except Post.DoesNotExists:
			#	Post.objects.create(username = media.user.username, instagram_id=media.id, post_url = media.link, media_type = media.type, tagname = tagname, media_url_lowres = media.get_low_resolution_url(), media_url_stdres = media.get_standard_resolution_url())

	except Exception, e:
		print 'recent_tag exception: %s' % e

def parse_instagram_update(update):
	tagName = update['object_id']
	print 'post tagged %s' %tagName
	#recent_tag(tagName)

def postupdate(request):
	if request.method == 'GET':
		challenge = request.GET.get('hub.challenge')
		if challenge:
			print challenge
			return HttpResponse(challenge)
	else:
		print 'callback post'
		reactor = subscriptions.SubscriptionsReactor()
		reactor.register_callback(subscriptions.SubscriptionType.TAG, parse_instagram_update)

		x_hub_signature = request.META.get('X-Hub-Signature')
		raw_response    = request.body

		try:
			reactor.process(CONFIG['client_secret'], raw_response, x_hub_signature)
		except subscriptions.SubscriptionVerifyError:
			print 'Instagram signature mismatch'

		return HttpResponse('Parsed instagram')