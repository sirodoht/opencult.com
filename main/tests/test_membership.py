import pytest
from django.test import Client

from main.models import Cult, Membership


@pytest.mark.django_db()
def test_membership_anon(django_user_model):
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Amsterdam',
    )
    c = Client()
    response = c.post('/membership/' + cult.slug + '/', {})
    assert response.status_code == 302


@pytest.mark.django_db()
def test_membership_nonmember(django_user_model):
    user = django_user_model.objects.create(username='mother')
    user.set_password('takeajacket')
    user.save()
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Amsterdam',
    )
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    assert logged_in
    response = c.post('/membership/' + cult.slug + '/', {})
    assert response.status_code == 302
    assert Membership.objects.get(user=user, cult=cult)


@pytest.mark.django_db()
def test_membership_member(django_user_model):
    user = django_user_model.objects.create(username='mother')
    user.set_password('takeajacket')
    user.save()
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Amsterdam',
    )
    Membership.objects.create(
        user=user,
        cult=cult,
        role=Membership.MEMBER,
    )
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    assert logged_in
    assert Membership.objects.filter(user=user, cult=cult).count() == 1
    response = c.post('/membership/' + cult.slug + '/delete/', {})
    assert response.status_code == 302
    assert Membership.objects.filter(user=user, cult=cult).count() == 0
