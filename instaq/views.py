
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from instaq.forms import EventForm , TagForm
from ig.models import Event, Tag, Post
from django.utils import timezone 
from ig.views import createTagSubscription, deleteTagSubscription

def home(request):
    user = request.user
    if user.is_authenticated():
	nowDate = timezone.now()
        event_form = EventForm()
        event_db = Event.objects.filter(owner=request.user).order_by('-created_time')
        event_list = []
        for ev in event_db:
        	e = {}
	        e["event"] = ev
        	e["tagform"] = TagForm(initial={'event_id': ev.pk})
        	e["tags"] = Tag.objects.filter(event = ev)
		e["posts"] = Post.objects.filter(event = ev)
	    	e["activated"] =  ev.start_time < nowDate and ev.stop_time > nowDate
            	event_list.append(e)

        return render_to_response('index.html', locals(), RequestContext(request))
    else:
        form = AuthenticationForm(request)
        return render_to_response('login.html', locals(), RequestContext(request))


def livegallery(request, eventname):
	return render_to_response('livegallery.html', locals(), RequestContext(request))


def login_user(request):
    # Process form data
    if request.method == 'POST':
        # Check if the username/password combination is valid and a User object is returned if it is
        user = authenticate(username=request.POST['username'], password=request.POST['password'])

        if user:
            login(request, user)
    return redirect(home)

@login_required
def logout_user(request):
    logout(request)
    return redirect(home)


@login_required
def create_event(request):
    try:
        if request.method == 'POST':
            form = EventForm(request.POST)
            if form.is_valid():
		print "creating event"
                new_event = Event(name=form.cleaned_data['name'], owner=request.user, start_time=form.cleaned_data['start_datetime'], stop_time=form.cleaned_data['stop_datetime'])
                new_event.save()
    except Exception, e:
        print 'create_event exception: %s' % e
    return redirect(home)


@login_required
def remove_event(request, eventid):
        try:
		#remove event's tags
		eventTags = Tag.objects.filter(event = eventid)
		for eventTag in eventTags:
			remove_tag_fromid(eventTag.pk)

		#removing event
            	eventtoremove = Event.objects.get(id=eventid)
            	print "removing event named %s" % eventtoremove.name
            	eventtoremove.delete()
        except Exception, e:
                print 'remove_event exception: %s' % e
        return redirect(home)


@login_required
def pause_event(request, eventid):
        try:
                currentEvent = Event.objects.get(pk = eventid)
                currentEvent.paused = True
		currentEvent.save()
        except Exception, e:
                print 'pause_event exception: %s' % e
        return redirect(home)


@login_required
def resume_event(request, eventid):
        try:    
                currentEvent = Event.objects.get(pk = eventid)
                currentEvent.paused = False
                currentEvent.save()
        except Exception, e:
                print 'resume_event exception: %s' % e
        return redirect(home)


@login_required
def create_tag(request):
    try:
        print "creating tag"
        if request.method == 'POST':
            form = TagForm(request.POST)
            if form.is_valid():
                current_ev = Event.objects.get(pk=form.cleaned_data['event_id'])
                new_tag = Tag(name=form.cleaned_data['name'], event=current_ev)
                new_tag.save()
		createTagSubscription(new_tag.name)
    except Exception, e:
        print 'create_tag exception: %s' % e
    return redirect(home)


def remove_subscription(tag):
	# Remove subscription only if it is the last event using this tag
	sameTags = Tag.objects.filter(name=tag)
	nowDate = timezone.now()
	anotherEventIsUsingSameTag = False
	for sameTag in sameTags:
		event = Event.objects.get(id=sameTag.event.pk)
		if event.start_time < nowDate and event.stop_time > nowDate and event.pk != tag.event.id:
			print "anotherEventIsUsingSameTag eventname: %s" %event.name
			anotherEventIsUsingSameTag = True
	if not anotherEventIsUsingSameTag:
		print "deleteTagSubscription named %s" % tag.name
		deleteTagSubscription(tag.name)		

def remove_tag_fromid(tagid):
	tagToRemove = Tag.objects.get(id=tagid)
        remove_subscription(tagToRemove)
        print "removing tag named %s from db" % tagToRemove.name
        tagToRemove.delete()


@login_required
def remove_tag(request, tagid):
        try:
		remove_tag_fromid(tagid)
        except Exception, e:
                print 'remove_tag exception: %s' % e
        return redirect(home)


