import os

import shortuuid
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as dj_login
from django.contrib.auth import logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.db.utils import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from opencult import settings

from .forms import (AddCultLeaderForm, CommentForm, CultAnnouncementForm, CultForm, EditCultForm, EditEventForm,
                    EmailForm, EventForm, UserForm)
from .helpers import email_login_link
from .models import Attendance, Comment, Cult, Event, Membership
from .tasks import announce_event, email_members


@require_safe
def index(request):
    if request.GET.get('city'):
        return city(request)

    now = timezone.now()
    events_list = Event.objects.filter(
        date__gte=now.date(),
    ).order_by('date', 'time')
    attending_events_list = Event.objects.filter(
        attendees__username=request.user.username,
        date__gte=now.date(),
    ).order_by('date', 'time')

    own_cults = None
    if request.user.is_authenticated:
        own_cults = Cult.objects.filter(membership__user=request.user, membership__role=Membership.LEADER)

    return render(request, 'main/index.html', {
        'color_class': 'purple-mixin',
        'dark_color_class': 'purple-dark-mixin',
        'nav_show_own_cults': True,
        'events_list': events_list,
        'attending_events_list': attending_events_list,
        'own_cults': own_cults,
    })


@require_safe
def city(request):
    city = request.GET.get('city')

    now = timezone.now()
    events_list = Event.objects.filter(
        cult__city=city,
        date__gte=now.date(),
    ).order_by('date', 'time')

    cults_list = Cult.objects.filter(city=city)

    own_cults = None
    if request.user.is_authenticated:
        own_cults = Cult.objects.filter(membership__user=request.user, membership__role=Membership.LEADER)

    return render(request, 'main/city.html', {
        'color_class': 'purple-mixin',
        'dark_color_class': 'purple-dark-mixin',
        'nav_show_own_cults': True,
        'events_list': events_list,
        'cults_list': cults_list,
        'own_cults': own_cults,
        'city': city,
    })


@require_safe
def login(request):
    if request.user.is_authenticated:
        return redirect('main:index')
    return render(request, 'main/login.html', {
        'color_class': 'yellow-mixin',
        'dark_color_class': 'yellow-dark-mixin',
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


@require_safe
@login_required
def logout(request):
    dj_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect(settings.LOGOUT_REDIRECT_URL)


@require_safe
def cult(request, cult_slug):
    try:
        cult = Cult.objects.get(slug=cult_slug)
    except Cult.DoesNotExist:
        raise Http404('Cult not found')

    now = timezone.now()
    upcoming_events_list = Event.objects.filter(
        cult=cult,
        date__gte=now.date(),
    ).order_by('-date', '-time')
    past_events_list = Event.objects.filter(
        cult=cult,
        date__lt=now.date(),
    ).order_by('-date', '-time')

    membership = None  # not authed
    if request.user.is_authenticated:
        try:
            membership = Membership.objects.get(user=request.user, cult=cult)
        except Membership.DoesNotExist:  # user is not member
            membership = None

    return render(request, 'main/cult.html', {
        'color_class': 'green-mixin',
        'dark_color_class': 'green-dark-mixin',
        'nav_show_edit_cult': True,
        'nav_show_new_event': True,
        'nav_show_join_cult': True,
        'nav_show_cult_announcement': True,
        'ld_cult': True,
        'cult': cult,
        'membership': membership,
        'upcoming_events_list': upcoming_events_list,
        'past_events_list': past_events_list,
    })


@require_safe
def event(request, cult_slug, event_slug):
    try:
        event = Event.objects.get(slug=event_slug)
    except Event.DoesNotExist:
        raise Http404('Event not found')

    cult = Cult.objects.get(slug=cult_slug)

    attendance = None  # not authed
    if request.user.is_authenticated:
        try:
            attendance = Attendance.objects.get(user=request.user, event=event)
        except Attendance.DoesNotExist:  # user is not attending
            attendance = None

    form = CommentForm()

    return render(request, 'main/event.html', {
        'color_class': 'blue-mixin',
        'dark_color_class': 'blue-dark-mixin',
        'nav_show_cult': True,
        'nav_show_edit_event': True,
        'nav_show_rsvp_event': True,
        'ld_event': True,
        'now': timezone.now(),
        'event': event,
        'cult': cult,
        'attendance': attendance,
        'form': form,
    })


@require_safe
def about(request):
    return render(request, 'main/about.html', {
        'color_class': 'purple-mixin',
        'dark_color_class': 'purple-dark-mixin',
        'nav_show_own_cults': True,
    })


@require_safe
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404('User not found')

    own_cults = None
    if request.user.is_authenticated:
        own_cults = Cult.objects.filter(membership__user=request.user, membership__role=Membership.LEADER)

    return render(request, 'main/profile.html', {
        'color_class': 'yellow-mixin',
        'dark_color_class': 'yellow-dark-mixin',
        'nav_show_own_cults': True,
        'own_cults': own_cults,
        'user': user,
    })


@require_http_methods(['HEAD', 'GET', 'POST'])
@login_required
def edit_profile(request, username):
    if request.method == 'POST':

        # user gets 403 on other profile post
        if request.user.username != username:
            return HttpResponse(status=403)

        form = UserForm(request.POST, instance=request.user, initial={'about': request.user.profile.about})
        if form.is_valid():
            updated_user = form.save(commit=False)
            updated_user.profile.about = form.cleaned_data['about']
            updated_user.save()
            messages.success(request, 'Profile updated')
            return redirect('main:edit_profile', updated_user.username)
    else:
        form = UserForm(instance=request.user, initial={'about': request.user.profile.about})

    return render(request, 'main/edit_profile.html', {
        'color_class': 'yellow-mixin',
        'dark_color_class': 'yellow-dark-mixin',
        'nav_show_own_cults': True,
        'nav_show_logout': True,
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
            return redirect('main:cult', cult_slug=new_cult.slug)
    else:
        form = CultForm()

    return render(request, 'main/new_cult.html', {
        'color_class': 'green-mixin',
        'dark_color_class': 'green-dark-mixin',
        'nav_show_own_cults': True,
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

            # send email announcement to members
            if not os.getenv('CIRCLECI'):
                for member in cult.members.all():
                    data = {
                        'domain': get_current_site(request).domain,
                        'member_email': member.email,
                        'event_title': new_event.title,
                        'event_date': new_event.date.strftime('%A, %B %-d, %Y'),
                        'event_time': new_event.time.strftime('%H:%I'),
                        'event_details': new_event.details,
                        'event_venue': new_event.venue,
                        'event_address': new_event.address,
                        'event_maps_url': new_event.maps_url,
                        'event_slug': new_event.slug,
                        'cult_name': cult.name,
                        'cult_city': cult.city,
                        'cult_slug': cult.slug,
                    }
                    announce_event.delay(data)

            return redirect('main:event', cult_slug=cult.slug, event_slug=new_event.slug)
    else:
        form = EventForm()

    return render(request, 'main/new_event.html', {
        'color_class': 'blue-mixin',
        'dark_color_class': 'blue-dark-mixin',
        'nav_show_own_cults': True,
        'nav_show_cult': True,
        'nav_show_new_event': True,
        'cult': cult,
        'form': form,
    })


@require_http_methods(['HEAD', 'GET', 'POST'])
@login_required
def edit_cult(request, cult_slug):
    try:
        cult = Cult.objects.get(slug=cult_slug)
    except Cult.DoesNotExist:
        raise Http404('Cult not found')

    if request.user not in cult.leaders_list:
        return HttpResponse(status=403)

    if request.method == 'POST':
        form = EditCultForm(request.POST, instance=cult)
        if form.is_valid():
            form.save()
            return redirect('main:cult', cult_slug=cult.slug)
    else:
        form = EditCultForm(instance=cult)

    return render(request, 'main/edit_cult.html', {
        'color_class': 'green-mixin',
        'dark_color_class': 'green-dark-mixin',
        'nav_show_cult': True,
        'nav_show_leader_add': True,
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
        'nav_show_cult': True,
        'nav_show_new_event': True,
        'cult': cult,
        'event': event,
        'form': form,
    })


@require_POST
@login_required
def membership(request, cult_slug):
    cult = Cult.objects.get(slug=cult_slug)
    Membership.objects.get_or_create(
        user=request.user,
        cult=cult,
        role=Membership.MEMBER,
    )
    return redirect('main:cult', cult_slug=cult.slug)


@require_POST
@login_required
def delete_membership(request, cult_slug):
    cult = Cult.objects.get(slug=cult_slug)

    # solo cult leader cannot unjoin
    if request.user in cult.leaders_list and cult.leaders_count == 1:
        return HttpResponse(status=403)

    Membership.objects.get(user=request.user, cult=cult).delete()
    return redirect('main:cult', cult_slug=cult.slug)


@require_POST
@login_required
def attendance(request, cult_slug, event_slug):
    event = Event.objects.get(slug=event_slug)

    # attendance cannot change on past events
    now = timezone.now()
    if event.date < now.date():
        return HttpResponse(status=403)

    Attendance.objects.get_or_create(
        user=request.user,
        event=event,
    )
    return redirect('main:event', cult_slug=cult_slug, event_slug=event.slug)


@require_POST
@login_required
def delete_attendance(request, cult_slug, event_slug):
    event = Event.objects.get(slug=event_slug)

    # attendance cannot change on past events
    now = timezone.now()
    if event.date < now.date():
        return HttpResponse(status=403)

    Attendance.objects.get(user=request.user, event=event).delete()
    return redirect('main:event', cult_slug=cult_slug, event_slug=event.slug)


@require_http_methods(['HEAD', 'GET', 'POST'])
@login_required
def cult_leader(request, cult_slug):
    cult = Cult.objects.get(slug=cult_slug)

    if request.user not in cult.leaders_list:
        return HttpResponse(status=403)

    if request.method == 'POST':
        form = AddCultLeaderForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, 'User "' + username + '" does not exist.')
                return redirect('main:cult_leader', cult.slug)
            membership, created = Membership.objects.get_or_create(
                user=user,
                cult=cult,
                role=Membership.LEADER,
            )
            if created:
                messages.success(request, username + ' has been added as leader at ' + cult.name + '.')
            else:
                messages.success(request, username + ' is already leader at ' + cult.name + '.')
            return redirect('main:cult', cult_slug=cult.slug)
    else:
        form = AddCultLeaderForm()

    return render(request, 'main/cult_leader.html', {
        'color_class': 'green-mixin',
        'dark_color_class': 'green-dark-mixin',
        'nav_show_cult': True,
        'nav_show_edit_cult': True,
        'cult': cult,
        'form': form,
    })


@require_http_methods(['POST'])
@login_required
def comment(request, cult_slug, event_slug):
    form = CommentForm(request.POST)
    if form.is_valid():
        body = form.cleaned_data.get('body')
        event = Event.objects.get(slug=event_slug)
        Comment.objects.create(
            event=event,
            author=request.user,
            body=body,
        )
        return redirect('main:event', cult_slug=event.cult.slug, event_slug=event.slug)


@require_http_methods(['HEAD', 'GET', 'POST'])
@login_required
def cult_announcement(request, cult_slug):
    cult = Cult.objects.get(slug=cult_slug)

    if request.user not in cult.leaders_list:
        return HttpResponse(status=403)

    if request.method == 'POST':
        form = CultAnnouncementForm(request.POST)
        if form.is_valid():

            # send email announcement to members
            if not os.getenv('CIRCLECI'):
                for member in cult.members.all():
                    data = {
                        'domain': get_current_site(request).domain,
                        'member_email': member.email,
                        'cult_name': cult.name,
                        'message': form.cleaned_data.get('message'),
                    }
                    email_members.delay(data)

            messages.success(request, 'The announcement has been emailed.')
            return redirect('main:cult', cult_slug=cult.slug)
    else:
        form = CultAnnouncementForm()

    return render(request, 'main/cult_announcement.html', {
        'color_class': 'green-mixin',
        'dark_color_class': 'green-dark-mixin',
        'nav_show_cult': True,
        'cult': cult,
        'form': form,
    })
