from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    date_of_birth = models.DateField(help_text='Use format "2000-01-31"',
                                     null=True)
    location = models.CharField(max_length=20, blank=True)
    sport_club = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)
    is_competitor = models.BooleanField(default=False)
    is_organizer = models.BooleanField(default=False)

    def __str__(self):
        return 'Profile user {}.'.format(self.username)

    def get_absolute_url(self):
        return reverse('account:user_detail',
                       args=[self.username])
