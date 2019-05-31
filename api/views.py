from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from main.models import Attendance, Group, Event


def docs(request):
    return render(request, "api/docs.html")


def groups(request):
    if request.GET.get("city"):
        return groups_city(request)

    groups = (
        Group.objects.all().order_by("name").values("name", "slug", "doctrine", "city")
    )
    groups_list = list(groups)
    for group in groups_list:
        group["members_count"] = Group.objects.get(slug=group["slug"]).members_count
    return JsonResponse(groups_list, safe=False)


def groups_city(request):
    city = request.GET.get("city")

    groups = (
        Group.objects.filter(city=city)
        .order_by("name")
        .values("name", "slug", "doctrine", "city")
    )
    groups_list = list(groups)
    for group in groups_list:
        group["members_count"] = Group.objects.get(slug=group["slug"]).members_count
    return JsonResponse(groups_list, safe=False)


def single_group(request, group_slug):
    group = Group.objects.get(slug=group_slug)
    group_dict = model_to_dict(group, fields=["name", "slug", "doctrine", "city"])
    group_dict["members"] = [m.username for m in group.members_list]
    events = Event.objects.filter(group=group).values_list("slug", flat=True)
    group_dict["events"] = list(events)
    return JsonResponse(group_dict, safe=False)


def events(request):
    if request.GET.get("city"):
        return events_city(request)

    now = timezone.now()
    events = (
        Event.objects.filter(date__gte=now.date())
        .order_by("title")
        .values(
            "title", "slug", "details", "date", "time", "venue", "address", "maps_url"
        )
    )
    events_list = list(events)
    for event in events_list:
        event["city"] = Event.objects.get(slug=event["slug"]).group.city
        event["attendees_count"] = Event.objects.get(slug=event["slug"]).attendees_count
    return JsonResponse(events_list, safe=False)


def events_city(request):
    city = request.GET.get("city")

    now = timezone.now()
    events = (
        Event.objects.filter(group__city=city, date__gte=now.date())
        .order_by("date", "time")
        .values(
            "title", "slug", "details", "date", "time", "venue", "address", "maps_url"
        )
    )
    events_list = list(events)
    for event in events_list:
        event["city"] = Event.objects.get(slug=event["slug"]).group.city
        event["attendees_count"] = Event.objects.get(slug=event["slug"]).attendees_count
    return JsonResponse(events_list, safe=False)


def single_event(request, event_slug):
    event = Event.objects.get(slug=event_slug)
    event_dict = model_to_dict(
        event,
        fields=[
            "title",
            "slug",
            "details",
            "date",
            "time",
            "venue",
            "address",
            "maps_url",
        ],
    )
    event_dict["group"] = event.group.slug
    event_dict["city"] = event.group.city
    attendees = Attendance.objects.filter(event=event).values_list(
        "user__username", flat=True
    )
    event_dict["attendees"] = list(attendees)
    return JsonResponse(event_dict, safe=False)
