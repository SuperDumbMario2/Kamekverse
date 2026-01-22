from django.contrib import admin
from .models import *

# Register your models here.
admin.site.site_header = "Kamekverse::Admin"
admin.site.register(Community)
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Post_Yeah)
admin.site.register(Platform_Badge)
admin.site.register(Comment)
admin.site.register(Title)
admin.site.register(Theme)
admin.site.register(Invite)
admin.site.register(Community_Favorite)