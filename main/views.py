import shortuuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.db.utils import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.text import slugify
from django.views import generic
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from main import forms, models, tasks
from opencult import settings


@require_safe
def index(request):
    if request.GET.get("city"):
        return city(request)

    now = timezone.now()
    events_list = models.Event.objects.filter(date__gte=now.date()).order_by(
        "date", "time"
    )
    attending_events_list = models.Event.objects.filter(
        attendees__username=request.user.username, date__gte=now.date()
    ).order_by("date", "time")

    own_groups = None
    if request.user.is_authenticated:
        own_groups = models.Group.objects.filter(
            membership__user=request.user, membership__role=models.Membership.ORGANIZER
        )

    return render(
        request,
        "main/index.html",
        {
            "nav_show_own_groups": True,
            "events_list": events_list,
            "attending_events_list": attending_events_list,
            "own_groups": own_groups,
        },
    )


@require_safe
def city(request):
    city = request.GET.get("city")

    now = timezone.now()
    events_list = models.Event.objects.filter(
        group__city=city, date__gte=now.date()
    ).order_by("date", "time")

    groups_list = models.Group.objects.filter(city=city)

    own_groups = None
    if request.user.is_authenticated:
        own_groups = models.Group.objects.filter(
            membership__user=request.user, membership__role=models.Membership.ORGANIZER
        )

    return render(
        request,
        "main/city.html",
        {
            "nav_show_own_groups": True,
            "events_list": events_list,
            "groups_list": groups_list,
            "own_groups": own_groups,
            "city": city,
        },
    )


class SignUp(generic.CreateView):
    form_class = forms.CustomUserCreationForm
    success_url = reverse_lazy("main:login")
    template_name = "registration/signup.html"


@require_safe
def group(request, group_slug):
    try:
        group = models.Group.objects.get(slug=group_slug)
    except models.Group.DoesNotExist:
        raise Http404("Group not found")

    now = timezone.now()
    upcoming_events_list = models.Event.objects.filter(
        group=group, date__gte=now.date()
    ).order_by("-date", "-time")
    past_events_list = models.Event.objects.filter(
        group=group, date__lt=now.date()
    ).order_by("-date", "-time")

    membership = None  # not authed
    if request.user.is_authenticated:
        try:
            membership = models.Membership.objects.get(user=request.user, group=group)
        except models.Membership.DoesNotExist:  # user is not member
            membership = None

    return render(
        request,
        "main/group.html",
        {
            "nav_show_group_admin": True,
            "nav_show_join_group": True,
            "ld_group": True,
            "group": group,
            "membership": membership,
            "upcoming_events_list": upcoming_events_list,
            "past_events_list": past_events_list,
        },
    )


@require_safe
def event(request, group_slug, event_slug):
    try:
        event = models.Event.objects.get(slug=event_slug)
    except models.Event.DoesNotExist:
        raise Http404("Event not found")

    group = models.Group.objects.get(slug=group_slug)

    attendance = None  # not authed
    if request.user.is_authenticated:
        try:
            attendance = models.Attendance.objects.get(user=request.user, event=event)
        except models.Attendance.DoesNotExist:  # user is not attending
            attendance = None

    form = forms.CommentCreationForm()

    return render(
        request,
        "main/event.html",
        {
            "nav_show_edit_event": True,
            "nav_show_rsvp_event": True,
            "ld_event": True,
            "now": timezone.now(),
            "event": event,
            "group": group,
            "attendance": attendance,
            "form": form,
        },
    )


@require_safe
def about(request):
    return render(request, "main/about.html", {"nav_show_own_groups": True})


@require_safe
def profile(request, username):
    try:
        user = models.CustomUser.objects.get(username=username)
    except models.CustomUser.DoesNotExist:
        raise Http404("User not found")

    own_groups = None
    if request.user.is_authenticated:
        own_groups = models.Group.objects.filter(
            membership__user=request.user, membership__role=models.Membership.ORGANIZER
        )

    return render(
        request,
        "main/profile.html",
        {"nav_show_own_groups": True, "own_groups": own_groups, "user": user},
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def edit_profile(request, username):
    if request.method == "POST":

        # user gets 403 on other profile post
        if request.user.username != username:
            return HttpResponse(status=403)

        form = forms.CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            updated_user = form.save()
            messages.success(request, "Profile updated")
            return redirect("main:profile", updated_user.username)
    else:
        form = forms.CustomUserChangeForm(instance=request.user)

    return render(
        request,
        "main/edit_profile.html",
        {"nav_show_own_groups": True, "nav_show_logout": True, "form": form},
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def new_group(request):
    if request.method == "POST":
        form = forms.GroupCreationForm(request.POST)
        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.slug = slugify(new_group.name)
            new_group.save()
            models.Membership.objects.create(
                group=new_group, user=request.user, role=models.Membership.ORGANIZER
            )
            return redirect("main:group", group_slug=new_group.slug)
    else:
        form = forms.GroupCreationForm()

    return render(
        request, "main/new_group.html", {"nav_show_own_groups": True, "form": form}
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def new_event(request, group_slug):
    group = models.Group.objects.get(slug=group_slug)
    if request.user not in group.organizers_list:
        return HttpResponse(status=403)
    if request.method == "POST":
        form = forms.EventCreationForm(request.POST)
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.slug = slugify(new_event.title)
            new_event.group = group
            try:
                new_event.save()
            except IntegrityError:
                uuid = shortuuid.ShortUUID(
                    "abdcefghkmnpqrstuvwxyzABDCEFGHKMNPQRSTUVWXYZ23456789"
                ).random(length=12)
                new_event.slug = slugify(new_event.title) + "-" + uuid
                new_event.save()
            models.Attendance.objects.create(event=new_event, user=request.user)

            # send email announcement to members
            for member in group.members.all():
                data = {
                    "protocol": request.scheme,
                    "domain": get_current_site(request).domain,
                    "member_email": member.email,
                    "event_title": new_event.title,
                    "event_date": new_event.date.strftime("%A, %B %-d, %Y"),
                    "event_time": new_event.time.strftime("%H:%I"),
                    "event_details": new_event.details,
                    "event_venue": new_event.venue,
                    "event_address": new_event.address,
                    "event_maps_url": new_event.maps_url,
                    "event_slug": new_event.slug,
                    "group_name": group.name,
                    "group_city": group.city,
                    "group_slug": group.slug,
                }
                tasks.email_async(
                    group.name + " announcement: " + new_event.title + " event",
                    render_to_string("main/announce_event_email.txt", {"data": data}),
                    settings.DEFAULT_FROM_EMAIL,
                    [data["member_email"]],
                )

            return redirect(
                "main:event", group_slug=group.slug, event_slug=new_event.slug
            )
    else:
        form = forms.EventCreationForm()

    return render(
        request,
        "main/new_event.html",
        {"nav_show_own_groups": True, "group": group, "form": form},
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def edit_group(request, group_slug):
    try:
        group = models.Group.objects.get(slug=group_slug)
    except models.Group.DoesNotExist:
        raise Http404("Group not found")

    if request.user not in group.organizers_list:
        return HttpResponse(status=403)

    if request.method == "POST":
        form = forms.GroupChangeForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("main:group", group_slug=group.slug)
    else:
        form = forms.GroupChangeForm(instance=group)

    return render(
        request,
        "main/edit_group.html",
        {"nav_show_organizer_add": True, "group": group, "form": form},
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def edit_event(request, group_slug, event_slug):
    group = models.Group.objects.get(slug=group_slug)
    event = models.Event.objects.get(slug=event_slug)

    if request.user not in group.organizers_list:
        return HttpResponse(status=403)

    if request.method == "POST":
        form = forms.EventChangeForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect("main:event", group_slug=group.slug, event_slug=event.slug)
    else:
        form = forms.EventChangeForm(instance=event)

    return render(
        request, "main/edit_event.html", {"group": group, "event": event, "form": form}
    )


@require_POST
@login_required
def membership(request, group_slug):
    group = models.Group.objects.get(slug=group_slug)
    models.Membership.objects.get_or_create(
        user=request.user, group=group, role=models.Membership.MEMBER
    )
    return redirect("main:group", group_slug=group.slug)


@require_POST
@login_required
def delete_membership(request, group_slug):
    group = models.Group.objects.get(slug=group_slug)

    # solo group organizer cannot unjoin
    if request.user in group.organizers_list and group.organizers_count == 1:
        return HttpResponse(status=403)

    models.Membership.objects.get(user=request.user, group=group).delete()
    return redirect("main:group", group_slug=group.slug)


@require_POST
@login_required
def attendance(request, group_slug, event_slug):
    event = models.Event.objects.get(slug=event_slug)

    # attendance cannot change on past events
    now = timezone.now()
    if event.date < now.date():
        return HttpResponse(status=403)

    models.Attendance.objects.get_or_create(user=request.user, event=event)
    return redirect("main:event", group_slug=group_slug, event_slug=event.slug)


@require_POST
@login_required
def delete_attendance(request, group_slug, event_slug):
    event = models.Event.objects.get(slug=event_slug)

    # attendance cannot change on past events
    now = timezone.now()
    if event.date < now.date():
        return HttpResponse(status=403)

    models.Attendance.objects.get(user=request.user, event=event).delete()
    return redirect("main:event", group_slug=group_slug, event_slug=event.slug)


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def group_organizer(request, group_slug):
    group = models.Group.objects.get(slug=group_slug)

    if request.user not in group.organizers_list:
        return HttpResponse(status=403)

    if request.method == "POST":
        form = forms.AddGroupOrganizerForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            try:
                user = models.CustomUser.objects.get(username=username)
            except models.CustomUser.DoesNotExist:
                messages.error(request, 'User "' + username + '" does not exist.')
                return redirect("main:group_organizer", group.slug)
            membership, created = models.Membership.objects.get_or_create(
                user=user, group=group, role=models.Membership.ORGANIZER
            )
            if created:
                messages.success(
                    request,
                    username + " has been added as organizer at " + group.name + ".",
                )
            else:
                messages.success(
                    request, username + " is already organizer at " + group.name + "."
                )
            return redirect("main:group", group_slug=group.slug)
    else:
        form = forms.AddGroupOrganizerForm()

    return render(request, "main/group_organizer.html", {"group": group, "form": form})


@require_http_methods(["POST"])
@login_required
def comment(request, group_slug, event_slug):
    form = forms.CommentCreationForm(request.POST)
    if form.is_valid():
        body = form.cleaned_data.get("body")
        event = models.Event.objects.get(slug=event_slug)
        models.Comment.objects.create(event=event, author=request.user, body=body)
        return redirect(
            "main:event", group_slug=event.group.slug, event_slug=event.slug
        )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def group_announcement(request, group_slug):
    group = models.Group.objects.get(slug=group_slug)

    if request.user not in group.organizers_list:
        return HttpResponse(status=403)

    if request.method == "POST":
        form = forms.GroupAnnouncementForm(request.POST)
        if form.is_valid():
            # send email announcement to members
            for member in group.members.all():
                tasks.email_async(
                    "Announcement from " + group.name,
                    render_to_string(
                        "main/group_announcement_email.txt",
                        {
                            "group_name": group.name,
                            "message": form.cleaned_data.get("message"),
                        },
                    ),
                    settings.DEFAULT_FROM_EMAIL,
                    [member.email],
                )
            messages.success(request, "The announcement has been emailed.")
            return redirect("main:group", group_slug=group.slug)
    else:
        form = forms.GroupAnnouncementForm()

    return render(
        request, "main/group_announcement.html", {"group": group, "form": form}
    )
