import base64
import json
import time

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.signing import Signer
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from opencult import settings

from .forms import EmailForm
from .models import Cult, Event, Membership


def index(request):
    events_list = Event.objects.order_by('-date')
    attending_events_list = Event.objects.filter(attendees__username=request.user.username).order_by('-date', 'time')
    return render(request, 'main/index.html', {
        'events_list': events_list,
        'attending_events_list': attending_events_list,
    })


def login(request):
    if request.user.is_authenticated:
        return redirect('main:index')
    return render(request, 'main/login.html', {
        'next': request.GET.get('next'),
    })


def token_post(request):
    if request.user.is_authenticated:
        messages.error(request, 'You are already logged in.')
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.GET.get('d'):
        # The user has clicked a login link.
        user = authenticate(token=request.GET['d'])
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, 'The login link was invalid or has expired. Please try to log in again.')
    elif request.method == 'POST':
        # The user has submitted the email form.
        form = EmailForm(request.POST)
        if form.is_valid():
            email_login_link(request, form.cleaned_data['email'])
            messages.success(request, 'Login email sent! Please check your inbox and click on the link.')
        else:
            messages.error(request, 'The email address was invalid. Please check the address and try again.')
    else:
        messages.error(request, 'The login link was invalid or has expired. Please try to log in again.')

    return redirect(settings.LOGIN_URL)


def email_login_link(request, email):
    current_site = get_current_site(request)

    # Create the signed structure containing the time and email address.
    email = email.lower().strip()
    data = {
        't': int(time.time()),
        'e': email,
    }
    data = json.dumps(data).encode('utf8')
    data = Signer().sign(base64.b64encode(data).decode('utf8'))

    # Send the link by email.
    send_mail(
        'Login link for Open Cult',
        render_to_string('main/token_auth_email.txt', {'current_site': current_site, 'data': data}, request=request),
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )


@login_required
def logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect(settings.LOGOUT_REDIRECT_URL)


def cult(request, cult_slug):
    cult = Cult.objects.get(slug=cult_slug)
    events_list = Event.objects.filter(cult=cult).order_by('-date', 'time')

    try:
        membership = Membership.objects.get(user=request.user, cult=cult)
    except Membership.DoesNotExist:
        membership = None

    return render(request, 'main/cult.html', {
        'cult': cult,
        'membership': membership,
        'events_list': events_list,
    })


def event(request, cult_slug, event_slug):
    event = Event.objects.get(slug=event_slug)
    return render(request, 'main/event.html', {
        'event': event,
    })


def about(request):
    return render(request, 'main/about.html')
