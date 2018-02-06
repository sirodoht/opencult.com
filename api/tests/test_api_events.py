import pytest
from django.test import Client

from main.models import Cult, Event


@pytest.mark.django_db()
def test_api_events():
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Bangkok',
    )
    event_1 = Event.objects.create(
        cult=cult,
        title='Westworld marathon',
        slug='westworld-marathon',
        details='Season 2 coming!',
        date='2118-02-02',
        time='18:00',
        venue='OK!Thess',
        address='Komotinis 2, 553 77',
        maps_url='https://goo.gl/maps/sample-link',
    )
    event_2 = Event.objects.create(
        cult=cult,
        title='Ready Player One Premiere',
        slug='ready-player-one',
        details='Go Parzival',
        date='2118-04-02',
        time='21:00',
        venue='City Cinemas',
        address='1 Sunshine Avenue, 534 77',
        maps_url='https://goo.gl/maps/sample-link',
    )
    c = Client()
    response = c.get('/api/events/')
    assert response.status_code == 200
    assert event_1.title.encode() in response.content
    assert event_1.slug.encode() in response.content
    assert event_1.details.encode() in response.content
    assert event_1.venue.encode() in response.content
    assert event_1.address.encode() in response.content
    assert event_1.maps_url.encode() in response.content
    assert event_2.title.encode() in response.content
    assert event_2.slug.encode() in response.content
    assert event_2.details.encode() in response.content
    assert event_2.venue.encode() in response.content
    assert event_2.address.encode() in response.content
    assert event_2.maps_url.encode() in response.content


@pytest.mark.django_db()
def test_api_event_single():
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Bangkok',
    )
    event = Event.objects.create(
        cult=cult,
        title='Ready Player One Premiere',
        slug='ready-player-one',
        details='Go Parzival',
        date='2118-04-02',
        time='21:00',
        venue='City Cinemas',
        address='1 Sunshine Avenue, 534 77',
        maps_url='https://goo.gl/maps/sample-link',
    )
    c = Client()
    response = c.get('/api/events/' + event.slug + '/')
    assert response.status_code == 200
    assert event.title.encode() in response.content
    assert event.slug.encode() in response.content
    assert event.details.encode() in response.content
    assert event.venue.encode() in response.content
    assert event.address.encode() in response.content
    assert event.maps_url.encode() in response.content


@pytest.mark.django_db()
def test_api_cult_city():
    cult = Cult.objects.create(
        name='Starman',
        slug='starman',
        doctrine='There\'s a starman waiting in the sky.',
        city='Cape Town',
    )
    event = Event.objects.create(
        cult=cult,
        title='Ready Player One Premiere',
        slug='ready-player-one',
        details='Go Parzival',
        date='2118-04-02',
        time='21:00',
        venue='City Cinemas',
        address='1 Sunshine Avenue, 534 77',
        maps_url='https://goo.gl/maps/sample-link',
    )
    c = Client()
    response = c.get('/api/events/?city=Cape Town')
    assert response.status_code == 200
    assert event.title.encode() in response.content
    assert event.slug.encode() in response.content
    assert event.details.encode() in response.content
    assert event.venue.encode() in response.content
    assert event.address.encode() in response.content
    assert event.maps_url.encode() in response.content
