from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from .forms import EventCreateForm
from .models import Event


@login_required
def event_create(request):
    if request.user.is_organizer:
        if request.method == 'POST':
            form = EventCreateForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                cd = form.cleaned_data
                new_item = form.save(commit=False)
                new_item.organizer_id = request.user.id
                new_item.save()
                messages.success(request, 'Event created.')
                return redirect(new_item.get_absolute_url())
        else:
            form = EventCreateForm()
        return render(request, 'events/event/create.html', {'form': form})
    return \
        HttpResponse('Sorry, to create an event you need to be the organizer.')


def detail_event(request, id, competition_name):
    event = get_object_or_404(Event, id=id, competition_name=competition_name)
    return render(request, 'events/event/detail.html',
                  {'event': event})


def event_list(request):
    events = Event.objects.all().order_by('competition_date').\
        select_related('organizer', 'competition_rank', 'discipline')
    paginator = Paginator(events, 3)
    page = request.GET.get('page')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)
    return render(request, 'events/event/list.html',
                  {'events': events, 'section': 'competition'})


@login_required
def event_edit(request, id, competition_name):
    event = Event.objects.get(id=id)
    if request.user == event.organizer:
        if request.method == "POST":
            event_form = EventCreateForm(instance=Event.objects.get(id=id),
                                         data=request.POST, files=request.FILES)
            if event_form.is_valid():
                event_form.save()
                event.refresh_from_db()
                competition_name = event.competition_name
                messages.success(request,
                                 'Edit event has finished successfully.')
                return redirect('competition:event_detail', id=id,
                                competition_name=competition_name)

        else:
            event_form = EventCreateForm(instance=Event.objects.get(id=id))

        return render(request, 'events/event/edit.html',
                      {'event_form': event_form})
    else:
        messages.warning(request,
                         "You don't have permission for editing this event.")
        return redirect('competition:event_detail', id=id,
                        competition_name=competition_name)


@login_required
def sign_up(request, id):
    event = Event.objects.get(id=id)
    all_competitors = event.competitors.count()
    date_today = date.today()
    user = request.user
    if user.is_competitor:
        if event.max_competitors:
            if event.max_competitors <= all_competitors:
                message = 'Sorry, registration is closed. Maximum numbers of ' \
                          'competitors has been reached. You cannot sign up.'
                messages.warning(request, message)
                return redirect('competition:event_detail', id=event.id,
                                competition_name=event.competition_name)
        if date_today <= event.applications_deadline:
            event.competitors.add(user)
            event.save()
            messages.success(request, 'You sign up correctly.')
            domain = get_current_site(request).domain
            sign_up_email_confirmation(domain=domain, event=event, user=user)
            return redirect('competition:event_detail', id=event.id,
                            competition_name=event.competition_name)
        else:
            message_deadline = 'Sorry, the deadline for registration has ' \
                               'expired. You cannot sign up.'
            messages.warning(request, message_deadline)
            return redirect('competition:event_detail', id=event.id,
                            competition_name=event.competition_name)
    else:
        message_user_not_competitor = \
            "Sorry, you aren't competitor. " \
            "If you want to sign up for the competition edit the profile."
        messages.warning(request, message_user_not_competitor)
        return redirect('competition:event_detail', id=event.id,
                        competition_name=event.competition_name)


@login_required
def resign(request, id):
    event = Event.objects.get(id=id)
    competitor = request.user
    event.competitors.remove(competitor)
    event.save()
    messages.success(request, 'You resign from competition.')
    return redirect('competition:event_detail', id=event.id,
                    competition_name=event.competition_name)


def sign_up_email_confirmation(domain, event, user):
    mail_subject = '{} team - registration for {}.'.\
        format(domain, event.competition_name)
    message = render_to_string('events/event/sign_up_confirmation.html', {
        'user': user,
        'domain': domain,
        'event': event,
    })
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()
