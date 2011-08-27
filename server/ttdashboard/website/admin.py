from website.models import *
from django.contrib import admin

class UserProfileAdmin(admin.ModelAdmin):
   search_fields = ['user__email']
   list_display = ('user', 'user_email', 'ttuid',)

admin.site.register(UserProfile, UserProfileAdmin)
