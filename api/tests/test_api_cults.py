import pytest
from django.test import Client

from main.models import Cult


@pytest.mark.django_db()
def test_api_cults():
    cult_1 = Cult.objects.create(
        name="Sweet Dreams",
        slug="sweet-dreams",
        doctrine="Hold your head up, keep your head up!",
        city="Amsterdam",
    )
    cult_2 = Cult.objects.create(
        name="Illumination Theory",
        slug="illumination-theory",
        doctrine="Consider this question, open your eyes.",
        city="Boston",
    )
    c = Client()
    response = c.get("/api/cults/")
    assert response.status_code == 200
    assert cult_1.name.encode() in response.content
    assert cult_1.slug.encode() in response.content
    assert cult_1.doctrine.encode() in response.content
    assert cult_1.city.encode() in response.content
    assert cult_2.name.encode() in response.content
    assert cult_2.slug.encode() in response.content
    assert cult_2.doctrine.encode() in response.content
    assert cult_2.city.encode() in response.content


@pytest.mark.django_db()
def test_api_cult_single():
    cult = Cult.objects.create(
        name="Sweet Dreams",
        slug="sweet-dreams",
        doctrine="Hold your head up, keep your head up!",
        city="Amsterdam",
    )
    c = Client()
    response = c.get("/api/cults/" + cult.slug + "/")
    assert response.status_code == 200
    assert cult.name.encode() in response.content
    assert cult.slug.encode() in response.content
    assert cult.doctrine.encode() in response.content
    assert cult.city.encode() in response.content


@pytest.mark.django_db()
def test_api_cult_city():
    cult = Cult.objects.create(
        name="Starman",
        slug="starman",
        doctrine="There's a starman waiting in the sky.",
        city="Cape Town",
    )
    c = Client()
    response = c.get("/api/cults/?city=Cape Town")
    assert response.status_code == 200
    assert cult.name.encode() in response.content
    assert cult.slug.encode() in response.content
    assert cult.doctrine.encode() in response.content
    assert cult.city.encode() in response.content
