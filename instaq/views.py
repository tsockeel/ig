
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from instaq.forms import EventForm
from ig.models import Event

def home(request):
	user = request.user
	if user.is_authenticated():
		event_form = EventForm()
		event_list = Event.objects.filter(owner=request.user)
		return render_to_response('index.html', locals(), RequestContext(request))
	else:
		form = AuthenticationForm(request)
		return render_to_response('login.html', locals(), RequestContext(request))

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
		print "creating event"
		if request.method == 'POST':
			print "post"
	        	form = EventForm(request.POST)
		        if form.is_valid():
				print "form valid"
				new_event = Event(name=form.cleaned_data['name'], owner=request.user)
				new_event.save()
	except Exception, e:
		print 'create_event exception: %s' % e
	return redirect(home)
