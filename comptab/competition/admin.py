from django.contrib import admin
from .models import Event, EventRank, EventDiscipline


class EventAdmin(admin.ModelAdmin):
    list_display = ['competition_name', 'competition_rank', 'city',
                    'competition_date']
    list_filter = ['city', 'organizer']


class EventRankAdmin(admin.ModelAdmin):
    list_display = ['competition_rank']


class EventDisciplineAdmin(admin.ModelAdmin):
    list_display = ['discipline']


admin.site.register(Event, EventAdmin)
admin.site.register(EventRank, EventRankAdmin)
admin.site.register(EventDiscipline, EventDisciplineAdmin)
