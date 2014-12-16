from django import forms
from datetimewidget.widgets import DateTimeWidget
from datetime import datetime

class EventForm(forms.Form):
    name = forms.CharField(max_length=50)
    dateTimeOptions = {
        'format': 'dd/mm/yyyy HH:ii',
        'autoclose': True,
        'clearBtn': False,
	'showMeridian': True}
    start_datetime = forms.DateTimeField(widget=DateTimeWidget(options = dateTimeOptions, usel10n=True, bootstrap_version=3))
    stop_datetime = forms.DateTimeField(widget=DateTimeWidget(options = dateTimeOptions, usel10n=True, bootstrap_version=3))

class TagForm(forms.Form):
    name = forms.CharField(max_length=50)
    event_id = forms.CharField(widget=forms.HiddenInput())
