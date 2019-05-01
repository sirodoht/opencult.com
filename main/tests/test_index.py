import pytest
from django.test import Client

from main.models import Cult, Event


@pytest.mark.django_db()
def test_events():
    cult = Cult.objects.create(
        name="Sweet Dreams",
        slug="sweet-dreams",
        doctrine="Hold your head up, keep your head up!",
        city="Amsterdam",
    )
    event = Event.objects.create(
        cult=cult,
        title="Westworld marathon",
        slug="westworld-marathon",
        details="Season 2 coming!",
        date="2118-02-02",
        time="18:00",
        venue="OK!Thess",
        address="Komotinis 2, 553 77",
        maps_url="https://goo.gl/maps/sample-link",
    )
    c = Client()
    response = c.get("/")
    assert response.status_code == 200
    assert cult.name.encode() in response.content
    assert cult.slug.encode() in response.content
    assert cult.city.encode() in response.content
    assert event.title.encode() in response.content
    assert event.slug.encode() in response.content
    assert event.venue.encode() in response.content
    assert event.address.encode() in response.content
    assert event.maps_url.encode() in response.content
