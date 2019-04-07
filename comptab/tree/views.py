from random import shuffle
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import TournamentTree, Match, Set
from competition.models import Event
from account.models import User


def tournament(request, id, competition_name):
    event = Event.objects.get(id=id)
    all_competitors = list(event.competitors.all())
    pairs_dict = match_pair(all_competitors)
    tourn = TournamentTree.objects.filter(event_id=event.id)
    return render(request, 'tree.html',
                  {'pairs': pairs_dict,
                   'tournament': tourn,
                   'event': event})


def match_pair(list_sorted_competitors):
    number_of_players = len(list_sorted_competitors)
    if number_of_players in (4, 8, 16, 32, 64, 128):
        pairs = {}
        first, second = 0, number_of_players -1
        for i in range(1, int(number_of_players/2)+1):
            pairs['pair'+str(i)] = (list_sorted_competitors[first],
                                    list_sorted_competitors[second])
            first += 1
            second -= 1
    return pairs


@login_required
def play_match(request, player1_id, player2_id, event_id):
    player1 = User.objects.get(id=player1_id)
    player2 = User.objects.get(id=player2_id)
    event = Event.objects.get(id=event_id)
    try:
        match = Match.objects.get(event_id=event, player1=player1,
                                  player2=player2)
    except Match.DoesNotExist:
        match = Match(event_id=event, player1=player1, player2=player2)
        match.save()
    match = Match.objects.get(event_id=event, player1=player1, player2=player2)

    won_sets = check_won_sets(match.player1_won_sets, match.player2_won_sets)
    if won_sets:
        if won_sets == 1:
            pass
        else:
            pass

    return render(request, 'match.html', {'player1': player1,
                                          'player2': player2,
                                          'match': match,
                                          'event':  event})


@login_required
def play_set(request, match_id, number_set=0):
    match = Match.objects.get(id=match_id)
    event = match.event_id
    player_1 = User.objects.get(id=match.player1_id)
    player_2 = User.objects.get(id=match.player2_id)
    number_set = match.player1_won_sets + match.player2_won_sets + 1
    try:
        set = Set.objects.get(match_id=match_id, number_set=number_set)
    except Set.DoesNotExist:
        number_set = match.player1_won_sets + match.player2_won_sets + 1
        set = Set(match_id=match, number_set=number_set)
        set.player_1_score = 0
        set.player_2_score = 0
        set.number_set = number_set
        set.save()

    return render(request, 'play_set.html', {'set': set,
                                             'match': match,
                                             'player_1': player_1,
                                             'player_2': player_2,
                                             'event': event})


@login_required
def add_points(request, set_id, player):
    game_set = Set.objects.get(id=set_id)
    match = game_set.match_id

    if player == '1':
        if game_set.player_1_score:
            game_set.player_1_score += 1.
            game_set.save()
        else:
            game_set.player_1_score = 1
            game_set.save()
    elif player == '2':
        if game_set.player_2_score:
            game_set.player_2_score += 1.
            game_set.save()
        else:
            game_set.player_2_score = 1
            game_set.save()

    set_result = check_result(game_set.player_1_score, game_set.player_2_score)
    if set_result:
        if set_result == 1:
            match.player1_won_sets += 1
            match.save()
        elif set_result == 2:
            match.player2_won_sets += 1
            match.save()
        return redirect('tournament:match', player1_id=match.player1.id,
                        player2_id=match.player2.id, event_id=match.event_id.id)

    else:
        return redirect('tournament:play_set', match_id=game_set.match_id.id)


def check_result(score_p1, score_p2):
    score_p1 = int(score_p1)
    score_p2 = int(score_p2)
    if score_p1 < 11 and score_p2 < 11:
        return False
    else:
        if score_p1 == 11 and score_p2 < 10:
            return 1
        elif score_p2 == 11 and score_p1 < 10:
            return 2
        elif score_p1 > 11 and (score_p1 - score_p2) == 2:
            return 1
        elif score_p2 > 11 and (score_p2 - score_p1) == 2:
            return 2


def check_won_sets(won_sets_player1, won_sets_player2):

    if won_sets_player1 == 3:
        return 1
    if won_sets_player2 == 3:
        return 2
    else:
        return False
