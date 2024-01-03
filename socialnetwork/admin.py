from django.contrib import admin
from .models import *

# Registering the created models into the admin site.
admin.site.register(UserProfile)
admin.site.register(UserPost)
admin.site.register(PostLike)
admin.site.register(UserComment)
admin.site.register(FriendNetwork)
admin.site.register(Chat)
