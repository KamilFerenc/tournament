from django.contrib import admin
from .models import TournamentTree


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['event_id', ]


admin.site.register(TournamentTree, ProfileAdmin)

