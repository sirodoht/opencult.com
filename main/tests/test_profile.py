import pytest
from django.test import Client

from main.models import Cult, Event, Membership, Profile


@pytest.mark.django_db()
def test_profile(django_user_model):
    user = django_user_model.objects.create(username='mother', email='setme@free.com')
    profile = Profile.objects.get(user=user)
    profile.about = 'Under the moonlight.'
    profile.save()
    cult_1 = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Amsterdam',
    )
    cult_2 = Cult.objects.create(
        name='The night is on fire',
        slug='night-on-fire',
        doctrine='What you say!',
        city='Barcelona',
    )
    Membership.objects.create(
        cult=cult_1,
        user=user,
        role=Membership.LEADER,
    )
    Membership.objects.create(
        cult=cult_2,
        user=user,
        role=Membership.MEMBER,
    )
    c = Client()
    response = c.get('/@' + user.username + '/')
    assert response.status_code == 200
    assert profile.about.encode() in response.content
    assert cult_1.name.encode() in response.content
    assert cult_2.name.encode() in response.content
