from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render

from main.models import Attendance, Cult, Event


def docs(request):
    return render(request, 'api/docs.html', {
        'color_class': 'purple-mixin',
        'dark_color_class': 'purple-dark-mixin',
    })


def cults(request):
    cults = Cult.objects.all().order_by('name').values('name', 'slug', 'doctrine', 'city')
    cults_list = list(cults)
    for cult in cults_list:
        cult['members_count'] = Cult.objects.get(slug=cult['slug']).members_count
    return JsonResponse(cults_list, safe=False)


def single_cult(request, cult_slug):
    cult = Cult.objects.get(slug=cult_slug)
    cult_dict = model_to_dict(cult, fields=['name', 'slug', 'doctrine', 'city'])
    cult_dict['members'] = [m.username for m in cult.members_list]
    events = Event.objects.filter(cult=cult).values_list('slug', flat=True)
    cult_dict['events'] = list(events)
    return JsonResponse(cult_dict, safe=False)


def events(request):
    events = Event.objects.all().order_by('title').values(
        'title',
        'slug',
        'details',
        'date',
        'time',
        'venue',
        'address',
        'maps_url',
    )
    events_list = list(events)
    for event in events_list:
        event['city'] = Event.objects.get(slug=event['slug']).cult.city
        event['attendees_count'] = Event.objects.get(slug=event['slug']).attendees_count
    return JsonResponse(events_list, safe=False)


def single_event(request, event_slug):
    event = Event.objects.get(slug=event_slug)
    event_dict = model_to_dict(
        event,
        fields=['title', 'slug', 'details', 'date', 'time', 'venue', 'address', 'maps_url']
    )
    event_dict['cult'] = event.cult.slug
    event_dict['city'] = event.cult.city
    attendees = Attendance.objects.filter(event=event).values_list('user__username', flat=True)
    event_dict['attendees'] = list(attendees)
    return JsonResponse(event_dict, safe=False)
