from django.contrib import admin
from .models import Event, EventRank, EventDiscipline, MaxEventCompetitors


class EventAdmin(admin.ModelAdmin):
    list_display = ['competition_name', 'competition_rank', 'city',
                    'competition_date']
    list_filter = ['city', 'organizer']


class EventRankAdmin(admin.ModelAdmin):
    list_display = ['competition_rank']


class EventDisciplineAdmin(admin.ModelAdmin):
    list_display = ['discipline']


class MaxCompetitorsAdmin(admin.ModelAdmin):
    list_display = ['max_competitors']


admin.site.register(Event, EventAdmin)
admin.site.register(EventRank, EventRankAdmin)
admin.site.register(EventDiscipline, EventDisciplineAdmin)
admin.site.register(MaxEventCompetitors, MaxCompetitorsAdmin)
