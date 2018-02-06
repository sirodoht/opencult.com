import pytest
from django.test import Client

from main.forms import AddCultLeaderForm, CultForm, EditCultForm
from main.models import Cult, Event, Membership


@pytest.mark.django_db()
def test_city_cult():
    cult = Cult.objects.create(
        name='SpaceX worshippers',
        slug='the-spacex-creed',
        doctrine='Mars, we\'re coming.',
        city='Los Angeles',
    )
    c = Client()
    response = c.get('/?city=Los Angeles')
    assert response.status_code == 200
    assert cult.name.encode() in response.content
    assert cult.slug.encode() in response.content
    assert cult.doctrine.encode() in response.content
    assert cult.city.encode() in response.content


@pytest.mark.django_db()
def test_city_cult():
    cult = Cult.objects.create(
        name='SpaceX worshippers',
        slug='the-spacex-creed',
        doctrine='Mars, we\'re coming.',
        city='Los Angeles',
    )
    event = Event.objects.create(
        cult=cult,
        title='SpaceX Falcon Heavy launch',
        slug='falcon-heavy-launch',
        details='Mars! Incoming!',
        date='2118-02-02',
        time='18:00',
        venue='SpaceX Fans HQ',
        address='2314 Olympus Str, 553 77',
        maps_url='https://goo.gl/maps/sample-link',
    )
    c = Client()
    response = c.get('/?city=Los Angeles')
    assert response.status_code == 200
    assert event.title.encode() in response.content
    assert event.slug.encode() in response.content
    assert event.venue.encode() in response.content
    assert event.address.encode() in response.content
    assert event.maps_url.encode() in response.content
