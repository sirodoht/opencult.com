import base64
import json
import time

import shortuuid
from django.contrib import messages
from django.contrib.auth import login as dj_login
from django.contrib.auth import logout as dj_logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.signing import Signer
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.views.decorators.http import (require_http_methods, require_POST,
                                          require_safe)

from opencult import settings

from .forms import (CultForm, EditCultForm, EditEventForm, EmailForm,
                    EventForm, UserForm)
from .models import Attendance, Cult, Event, Membership


@require_safe
def index(request):
    events_list = Event.objects.order_by('-date')
    attending_events_list = Event.objects.filter(attendees__username=request.user.username).order_by('-date', 'time')

    my_cults = None
    if request.user.is_authenticated:
        my_cults = Cult.objects.filter(membership__user=request.user, membership__role=Membership.LEADER)

    return render(request, 'main/index.html', {
        'color_class': 'purple-mixin',
        'dark_color_class': 'purple-dark-mixin',
        'events_list': events_list,
        'attending_events_list': attending_events_list,
        'my_cults': my_cults,
    })


@require_safe
def login(request):
    if request.user.is_authenticated:
        return redirect('main:index')
    return render(request, 'main/login.html', {
        'next': request.GET.get('next'),
    })


@require_http_methods(['HEAD', 'GET', 'POST'])
def token_post(request):
    if request.user.is_authenticated:
        messages.error(request, 'You are already logged in.')
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.GET.get('d'):
        # The user has clicked a login link.
        user = authenticate(token=request.GET['d'])
        if user is not None:
            dj_login(request, user)
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


@require_safe
@login_required
def logout(request):
    dj_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect(settings.LOGOUT_REDIRECT_URL)


@require_safe
def cult(request, cult_slug):
    cult = Cult.objects.get(slug=cult_slug)
    events_list = Event.objects.filter(cult=cult).order_by('-date', 'time')

    membership = None  # not authed
    if request.user.is_authenticated:
        try:
            membership = Membership.objects.get(user=request.user, cult=cult)
        except Membership.DoesNotExist:  # user is not member
            membership = None

    return render(request, 'main/cult.html', {
        'color_class': 'green-mixin',
        'dark_color_class': 'green-dark-mixin',
        'cult': cult,
        'membership': membership,
        'events_list': events_list,
    })


@require_safe
def event(request, cult_slug, event_slug):
    event = Event.objects.get(slug=event_slug)
    cult = Cult.objects.get(slug=cult_slug)

    membership = None  # not authed
    if request.user.is_authenticated:
        try:
            membership = Membership.objects.get(user=request.user, cult=cult)
        except Membership.DoesNotExist:  # user is not member
            membership = None

    attendance = None  # not authed
    if request.user.is_authenticated:
        try:
            attendance = Attendance.objects.get(user=request.user, event=event)
        except Attendance.DoesNotExist:  # user is not attending
            attendance = None

    return render(request, 'main/event.html', {
        'color_class': 'blue-mixin',
        'dark_color_class': 'blue-dark-mixin',
        'event': event,
        'cult': cult,
        'membership': membership,
        'attendance': attendance,
    })


@require_safe
def about(request):
    return render(request, 'main/about.html', {
        'color_class': 'purple-mixin',
        'dark_color_class': 'purple-dark-mixin',
    })


@require_safe
def profile(request, username):
    user = User.objects.get(username=username)
    return render(request, 'main/profile.html', {
        'color_class': 'yellow-mixin',
        'dark_color_class': 'yellow-dark-mixin',
        'user': user,
    })


@require_http_methods(['HEAD', 'GET', 'POST'])
def edit_profile(request, username):
    user = User.objects.get(username=username)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user, initial={'about': user.profile.about})
        if form.is_valid():
            updated_user = form.save(commit=False)
            updated_user.profile.about = form.cleaned_data['about']
            updated_user.save()
            messages.success(request, 'Profile updated')
            return redirect('main:edit_profile', updated_user.username)
    else:
        form = UserForm(instance=user, initial={'about': user.profile.about})

    return render(request, 'main/edit_profile.html', {
        'color_class': 'yellow-mixin',
        'dark_color_class': 'yellow-dark-mixin',
        'form': form,
    })


@require_http_methods(['HEAD', 'GET', 'POST'])
@login_required
def new_cult(request):
    if request.method == 'POST':
        form = CultForm(request.POST)
        if form.is_valid():
            new_cult = form.save(commit=False)
            new_cult.slug = slugify(new_cult.name)
            new_cult.save()
            Membership.objects.create(
                cult=new_cult,
                user=request.user,
                role=Membership.LEADER,
            )
            return redirect('main:new_cult')
    else:
        form = CultForm()

    return render(request, 'main/new_cult.html', {
        'color_class': 'green-mixin',
        'dark_color_class': 'green-dark-mixin',
        'form': form,
    })


@require_http_methods(['HEAD', 'GET', 'POST'])
@login_required
def new_event(request, cult_slug):
    cult = Cult.objects.get(slug=cult_slug)
    if request.user not in cult.leaders_list:
        return HttpResponse(status=403)
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.slug = slugify(new_event.title)
            new_event.cult = cult
            try:
                new_event.save()
            except IntegrityError:
                uuid = shortuuid.ShortUUID('abdcefghkmnpqrstuvwxyzABDCEFGHKMNPQRSTUVWXYZ23456789').random(length=12)
                new_event.slug = slugify(new_event.title) + '-' + uuid
                new_event.save()
            Attendance.objects.create(
                event=new_event,
                user=request.user,
            )
            return redirect('main:event', cult_slug=cult.slug, event_slug=new_event.slug)
    else:
        form = EventForm()

    return render(request, 'main/new_event.html', {
        'color_class': 'blue-mixin',
        'dark_color_class': 'blue-dark-mixin',
        'cult': cult,
        'form': form,
    })


@require_http_methods(['HEAD', 'GET', 'POST'])
@login_required
def edit_cult(request, cult_slug):
    cult = Cult.objects.get(slug=cult_slug)

    if request.user not in cult.leaders_list:
        return HttpResponse(status=403)

    if request.method == 'POST':
        form = EditCultForm(request.POST, instance=cult)
        if form.is_valid():
            form.save()
            return redirect('main:cult', cult_slug=cult.slug)
    else:
        cult = Cult.objects.get(slug=cult_slug)
        form = EditCultForm(instance=cult)

    return render(request, 'main/edit_cult.html', {
        'color_class': 'green-mixin',
        'dark_color_class': 'green-dark-mixin',
        'cult': cult,
        'form': form,
    })


@require_http_methods(['HEAD', 'GET', 'POST'])
@login_required
def edit_event(request, cult_slug, event_slug):
    cult = Cult.objects.get(slug=cult_slug)
    event = Event.objects.get(slug=event_slug)

    if request.user not in cult.leaders_list:
        return HttpResponse(status=403)

    if request.method == 'POST':
        form = EditEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('main:event', cult_slug=cult.slug, event_slug=event.slug)
    else:
        form = EditEventForm(instance=event)

    return render(request, 'main/edit_event.html', {
        'color_class': 'blue-mixin',
        'dark_color_class': 'blue-dark-mixin',
        'cult': cult,
        'event': event,
        'form': form,
    })


@require_POST
@login_required
def membership(request, cult_slug):
    cult = Cult.objects.get(slug=cult_slug)
    Membership.objects.create(
        user=request.user,
        cult=cult,
        role=Membership.MEMBER,
    )
    return redirect('main:cult', cult_slug=cult.slug)


@require_POST
@login_required
def delete_membership(request, cult_slug):
    cult = Cult.objects.get(slug=cult_slug)
    Membership.objects.get(user=request.user, cult=cult).delete()
    return redirect('main:cult', cult_slug=cult.slug)


@require_POST
@login_required
def attendance(request, cult_slug, event_slug):
    event = Event.objects.get(slug=event_slug)
    Attendance.objects.create(
        user=request.user,
        event=event,
    )
    return redirect('main:event', cult_slug=cult_slug, event_slug=event.slug)


@require_POST
@login_required
def delete_attendance(request, cult_slug, event_slug):
    event = Event.objects.get(slug=event_slug)
    Attendance.objects.get(user=request.user, event=event).delete()
    return redirect('main:event', cult_slug=cult_slug, event_slug=event.slug)
