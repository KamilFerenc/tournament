from django.db import models
from django.conf import settings
from django.urls import reverse


class EventRank(models.Model):

    competition_rank = models.CharField(max_length=30)
    cup = models.ImageField(upload_to='cups/', blank=True)

    def __str__(self):
        return "{}".format(self.competition_rank)


class EventDiscipline(models.Model):

    discipline = models.CharField(max_length=30)

    def __str__(self):
        return "{}".format(self.discipline)


class Event(models.Model):

    competition_name = models.CharField(max_length=50)
    competition_rank = models.ForeignKey(EventRank, on_delete=models.CASCADE)
    discipline = models.ForeignKey(EventDiscipline, on_delete=models.CASCADE)
    competition_date = models.DateField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  related_name='event_created')
    description = models.TextField(blank=True)
    applications_deadline = models.DateField()
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    number = models.PositiveIntegerField()
    poster = models.ImageField(upload_to='posters/%Y/%m/%d',
                               blank=True, null=True)
    competitors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                         related_name='event_competitors')
    max_competitors = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ('-competition_date',)

    def __str__(self):
        return 'Competition {}.'.format(self.competition_name)

    def get_absolute_url(self):
        return reverse('competition:event_detail',
                       args=[self.id, self.competition_name])
