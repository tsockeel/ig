from django.contrib import admin
from ig.models import Event, Tag, Recording, Post

# Register your models here.

admin.site.register(Event)
admin.site.register(Tag)
admin.site.register(Recording)
admin.site.register(Post)
