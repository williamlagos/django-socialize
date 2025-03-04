from django.contrib import admin
from .models import ActivityPubObject, ActivityPubActivity

admin.site.register(ActivityPubObject)
admin.site.register(ActivityPubActivity)
