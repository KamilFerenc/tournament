from django.db import models
from competition.models import Event
from account.models import User


class TournamentTree(models.Model):

    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    round_1_competitors = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='round_1_competitors',
        null=True, blank=True)
    round_1_won_sets = models.PositiveIntegerField(null=True, blank=True)

    round_2_competitors = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='round_2_competitors',
        null=True, blank=True)
    round_2_won_sets = models.PositiveIntegerField(null=True, blank=True)

    round_3_competitors = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='round_3_competitors',
        null=True, blank=True)
    round_3_won_sets = models.PositiveIntegerField(null=True, blank=True)

    round_4_competitors = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='round_4_competitors',
        null=True, blank=True)
    round_4_won_sets = models.PositiveIntegerField(null=True, blank=True)

    round_5_competitors = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='round_5_competitors',
        null=True, blank=True)
    round_5_won_sets = models.PositiveIntegerField(null=True, blank=True)

    round_6_competitors = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='round_6_competitors',
        null=True, blank=True)
    round_6_won_sets = models.PositiveIntegerField(null=True, blank=True)

    round_7_competitors = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='round_7_competitors',
        null=True, blank=True)
    round_7_won_sets = models.PositiveIntegerField(null=True, blank=True)

    round_8_competitors = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='round_8_competitors',
        null=True, blank=True)
    round_8_won_sets = models.PositiveIntegerField(null=True, blank=True)


class Match(models.Model):
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='player2')
    player1_won_sets = models.PositiveIntegerField(default=0)
    player2_won_sets = models.PositiveIntegerField(default=0)
    played = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ('-played',)

        def __str__(self):
            return 'Match {} vs {}'.format(self.player1.username,
                                           self.player2.username)


class Set(models.Model):
    match_id = models.ForeignKey(Match, on_delete=models.CASCADE)
    player_1_score = models.PositiveIntegerField(blank=True, null=True)
    player_2_score = models.PositiveIntegerField(blank=True, null=True)
    number_set = models.PositiveIntegerField()

