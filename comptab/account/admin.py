from django.contrib import admin
from .models import User


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'location']
    list_filter = ['location', 'date_joined']


admin.site.register(User, ProfileAdmin)
