from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegistrationForm, UserEditForm
from .models import User
from .tokens import account_activation_token
from competition.models import Event


def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(data=request.POST, files=request.FILES)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.is_active = False
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            current_site = get_current_site(request)
            send_email_confirmation(current_site, new_user)
            return HttpResponse('Please check your email to complete the '
                                'registration.')
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


def send_email_confirmation(current_site, new_user):
    mail_subject = 'Activate your social website account'
    message = render_to_string('account/acc_active_email.html', {
        'user': new_user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(new_user.pk)).decode(),
        'token': account_activation_token.make_token(new_user),
    })
    to_email = new_user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        new_user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError):
        new_user = None
    if new_user is not None and \
            account_activation_token.check_token(new_user, token):
        new_user.is_active = True
        new_user.save()
        login(request, new_user)
        messages.success(request, 'Thank you for activate your account.')
        return redirect('account:dashboard')
    else:
        return HttpResponse('Activation link is invalid.')

@login_required
def dashboard(request):
    user = request.user
    sign_up_events = \
        Event.objects.filter(competitors=user).order_by('competition_date')
    organized_events = \
        Event.objects.filter(organizer_id=user.id).order_by('competition_date')
    return render(request, 'account/dashboard.html',
                  {'sign_up_events': sign_up_events,
                   'organized_events': organized_events})


@login_required
def edit(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST,
                                 files=request.FILES)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your changes have been saved.')
            return redirect('account:dashboard')

    else:
        user_form = UserEditForm(instance=request.user)

    return render(request, 'account/edit.html', {'user_form': user_form})


@login_required
def competitors_list(request):
    users = User.objects.filter(
        is_active=True, is_competitor=True).exclude(id=request.user.id)
    return render(request, 'account/user/list.html', {'users': users,
                                                      'section': 'competitors'})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    sign_up_event = Event.objects.filter(competitors=user)
    return render(request, 'account/user/detail.html',
                  {'user': user, 'section': 'people',
                   'events': sign_up_event})
