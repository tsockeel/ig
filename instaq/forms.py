from django import forms

class EventForm(forms.Form):
    name = forms.CharField(max_length=30)
