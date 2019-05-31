import shortuuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.db.utils import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.text import slugify
from django.views import generic
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from main.forms import (
    AddGroupLeaderForm,
    CommentForm,
    GroupAnnouncementForm,
    GroupForm,
    CustomUserCreationForm,
    EditGroupForm,
    EditEventForm,
    EventForm,
)
from main.models import Attendance, Comment, Group, Event, Membership, CustomUser
from main.tasks import announce_event, email_members


@require_safe
def index(request):
    if request.GET.get("city"):
        return city(request)

    now = timezone.now()
    events_list = Event.objects.filter(date__gte=now.date()).order_by("date", "time")
    attending_events_list = Event.objects.filter(
        attendees__username=request.user.username, date__gte=now.date()
    ).order_by("date", "time")

    own_groups = None
    if request.user.is_authenticated:
        own_groups = Group.objects.filter(
            membership__user=request.user, membership__role=Membership.LEADER
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
    events_list = Event.objects.filter(group__city=city, date__gte=now.date()).order_by(
        "date", "time"
    )

    groups_list = Group.objects.filter(city=city)

    own_groups = None
    if request.user.is_authenticated:
        own_groups = Group.objects.filter(
            membership__user=request.user, membership__role=Membership.LEADER
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
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


@require_safe
def group(request, group_slug):
    try:
        group = Group.objects.get(slug=group_slug)
    except Group.DoesNotExist:
        raise Http404("Group not found")

    now = timezone.now()
    upcoming_events_list = Event.objects.filter(
        group=group, date__gte=now.date()
    ).order_by("-date", "-time")
    past_events_list = Event.objects.filter(group=group, date__lt=now.date()).order_by(
        "-date", "-time"
    )

    membership = None  # not authed
    if request.user.is_authenticated:
        try:
            membership = Membership.objects.get(user=request.user, group=group)
        except Membership.DoesNotExist:  # user is not member
            membership = None

    return render(
        request,
        "main/group.html",
        {
            "nav_show_edit_group": True,
            "nav_show_new_event": True,
            "nav_show_join_group": True,
            "nav_show_group_announcement": True,
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
        event = Event.objects.get(slug=event_slug)
    except Event.DoesNotExist:
        raise Http404("Event not found")

    group = Group.objects.get(slug=group_slug)

    attendance = None  # not authed
    if request.user.is_authenticated:
        try:
            attendance = Attendance.objects.get(user=request.user, event=event)
        except Attendance.DoesNotExist:  # user is not attending
            attendance = None

    form = CommentForm()

    return render(
        request,
        "main/event.html",
        {
            "nav_show_group": True,
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
        user = CustomUser.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User not found")

    own_groups = None
    if request.user.is_authenticated:
        own_groups = Group.objects.filter(
            membership__user=request.user, membership__role=Membership.LEADER
        )

    return render(
        request,
        "main/profile.html",
        {"nav_show_own_groups": True, "own_groups": own_groups, "user": user},
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def edit_profile(request, username):
    # if request.method == "POST":

    #     # user gets 403 on other profile post
    #     if request.user.username != username:
    #         return HttpResponse(status=403)

    #     form = UserForm(
    #         request.POST,
    #         instance=request.user,
    #         initial={"about": request.user.profile.about},
    #     )
    #     if form.is_valid():
    #         updated_user = form.save(commit=False)
    #         updated_user.profile.about = form.cleaned_data["about"]
    #         updated_user.save()
    #         messages.success(request, "Profile updated")
    #         return redirect("main:edit_profile", updated_user.username)
    # else:
    #     form = UserForm(
    #         instance=request.user, initial={"about": request.user.profile.about}
    #     )

    return render(
        request,
        "main/edit_profile.html",
        {"nav_show_own_groups": True, "nav_show_logout": True},
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def new_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.slug = slugify(new_group.name)
            new_group.save()
            Membership.objects.create(
                group=new_group, user=request.user, role=Membership.LEADER
            )
            return redirect("main:group", group_slug=new_group.slug)
    else:
        form = GroupForm()

    return render(
        request, "main/new_group.html", {"nav_show_own_groups": True, "form": form}
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def new_event(request, group_slug):
    group = Group.objects.get(slug=group_slug)
    if request.user not in group.leaders_list:
        return HttpResponse(status=403)
    if request.method == "POST":
        form = EventForm(request.POST)
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
            Attendance.objects.create(event=new_event, user=request.user)

            # send email announcement to members
            for member in group.members.all():
                data = {
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
                announce_event.delay(data)

            return redirect(
                "main:event", group_slug=group.slug, event_slug=new_event.slug
            )
    else:
        form = EventForm()

    return render(
        request,
        "main/new_event.html",
        {
            "nav_show_own_groups": True,
            "nav_show_group": True,
            "nav_show_new_event": True,
            "group": group,
            "form": form,
        },
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def edit_group(request, group_slug):
    try:
        group = Group.objects.get(slug=group_slug)
    except Group.DoesNotExist:
        raise Http404("Group not found")

    if request.user not in group.leaders_list:
        return HttpResponse(status=403)

    if request.method == "POST":
        form = EditGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("main:group", group_slug=group.slug)
    else:
        form = EditGroupForm(instance=group)

    return render(
        request,
        "main/edit_group.html",
        {
            "nav_show_group": True,
            "nav_show_leader_add": True,
            "group": group,
            "form": form,
        },
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def edit_event(request, group_slug, event_slug):
    group = Group.objects.get(slug=group_slug)
    event = Event.objects.get(slug=event_slug)

    if request.user not in group.leaders_list:
        return HttpResponse(status=403)

    if request.method == "POST":
        form = EditEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect("main:event", group_slug=group.slug, event_slug=event.slug)
    else:
        form = EditEventForm(instance=event)

    return render(
        request,
        "main/edit_event.html",
        {
            "nav_show_group": True,
            "nav_show_new_event": True,
            "group": group,
            "event": event,
            "form": form,
        },
    )


@require_POST
@login_required
def membership(request, group_slug):
    group = Group.objects.get(slug=group_slug)
    Membership.objects.get_or_create(
        user=request.user, group=group, role=Membership.MEMBER
    )
    return redirect("main:group", group_slug=group.slug)


@require_POST
@login_required
def delete_membership(request, group_slug):
    group = Group.objects.get(slug=group_slug)

    # solo group leader cannot unjoin
    if request.user in group.leaders_list and group.leaders_count == 1:
        return HttpResponse(status=403)

    Membership.objects.get(user=request.user, group=group).delete()
    return redirect("main:group", group_slug=group.slug)


@require_POST
@login_required
def attendance(request, group_slug, event_slug):
    event = Event.objects.get(slug=event_slug)

    # attendance cannot change on past events
    now = timezone.now()
    if event.date < now.date():
        return HttpResponse(status=403)

    Attendance.objects.get_or_create(user=request.user, event=event)
    return redirect("main:event", group_slug=group_slug, event_slug=event.slug)


@require_POST
@login_required
def delete_attendance(request, group_slug, event_slug):
    event = Event.objects.get(slug=event_slug)

    # attendance cannot change on past events
    now = timezone.now()
    if event.date < now.date():
        return HttpResponse(status=403)

    Attendance.objects.get(user=request.user, event=event).delete()
    return redirect("main:event", group_slug=group_slug, event_slug=event.slug)


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def group_leader(request, group_slug):
    group = Group.objects.get(slug=group_slug)

    if request.user not in group.leaders_list:
        return HttpResponse(status=403)

    if request.method == "POST":
        form = AddGroupLeaderForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            try:
                user = CustomUser.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, 'User "' + username + '" does not exist.')
                return redirect("main:group_leader", group.slug)
            membership, created = Membership.objects.get_or_create(
                user=user, group=group, role=Membership.LEADER
            )
            if created:
                messages.success(
                    request,
                    username + " has been added as leader at " + group.name + ".",
                )
            else:
                messages.success(
                    request, username + " is already leader at " + group.name + "."
                )
            return redirect("main:group", group_slug=group.slug)
    else:
        form = AddGroupLeaderForm()

    return render(
        request,
        "main/group_leader.html",
        {"nav_show_group": True, "nav_show_edit_group": True, "group": group, "form": form},
    )


@require_http_methods(["POST"])
@login_required
def comment(request, group_slug, event_slug):
    form = CommentForm(request.POST)
    if form.is_valid():
        body = form.cleaned_data.get("body")
        event = Event.objects.get(slug=event_slug)
        Comment.objects.create(event=event, author=request.user, body=body)
        return redirect("main:event", group_slug=event.group.slug, event_slug=event.slug)


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def group_announcement(request, group_slug):
    group = Group.objects.get(slug=group_slug)

    if request.user not in group.leaders_list:
        return HttpResponse(status=403)

    if request.method == "POST":
        form = GroupAnnouncementForm(request.POST)
        if form.is_valid():

            # send email announcement to members
            for member in group.members.all():
                data = {
                    "domain": get_current_site(request).domain,
                    "member_email": member.email,
                    "group_name": group.name,
                    "message": form.cleaned_data.get("message"),
                }
                email_members.delay(data)

            messages.success(request, "The announcement has been emailed.")
            return redirect("main:group", group_slug=group.slug)
    else:
        form = GroupAnnouncementForm()

    return render(
        request,
        "main/group_announcement.html",
        {"nav_show_group": True, "group": group, "form": form},
    )
