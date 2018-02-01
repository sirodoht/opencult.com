import pytest
from django.test import Client

from main.models import Attendance, Cult, Event, Membership


@pytest.mark.django_db()
def test_attendance_anon(django_user_model):
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Amsterdam',
    )
    event = Event.objects.create(
        cult=cult,
        title='Westworld marathon',
        slug='westworld-marathon',
        details='Season 2 coming!',
        date='2018-02-02',
        time='18:00',
        venue='OK!Thess',
        address='Komotinis 2, 553 77',
        maps_url='https://goo.gl/maps/sample-link',
    )
    c = Client()
    response = c.post('/attendance/' + cult.slug + '/' + event.slug + '/', {})
    assert response.status_code == 302
    assert Attendance.objects.filter().count() == 0


@pytest.mark.django_db()
def test_attendance_nonmember(django_user_model):
    user = django_user_model.objects.create(username='mother')
    user.set_password('takeajacket')
    user.save()
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Amsterdam',
    )
    event = Event.objects.create(
        cult=cult,
        title='Westworld marathon',
        slug='westworld-marathon',
        details='Season 2 coming!',
        date='2018-02-02',
        time='18:00',
        venue='OK!Thess',
        address='Komotinis 2, 553 77',
        maps_url='https://goo.gl/maps/sample-link',
    )
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    assert logged_in
    response = c.post('/attendance/' + cult.slug + '/' + event.slug + '/', {})
    assert response.status_code == 302
    assert Attendance.objects.filter().count() == 1


@pytest.mark.django_db()
def test_attendance_member(django_user_model):
    user = django_user_model.objects.create(username='mother')
    user.set_password('takeajacket')
    user.save()
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Amsterdam',
    )
    event = Event.objects.create(
        cult=cult,
        title='Westworld marathon',
        slug='westworld-marathon',
        details='Season 2 coming!',
        date='2018-02-02',
        time='18:00',
        venue='OK!Thess',
        address='Komotinis 2, 553 77',
        maps_url='https://goo.gl/maps/sample-link',
    )
    Membership.objects.create(
        user=user,
        cult=cult,
        role=Membership.MEMBER,
    )
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    assert logged_in
    response = c.post('/attendance/' + cult.slug + '/' + event.slug + '/', {})
    assert response.status_code == 302
    assert Attendance.objects.filter().count() == 1


@pytest.mark.django_db()
def test_attendance_member_delete(django_user_model):
    user = django_user_model.objects.create(username='mother')
    user.set_password('takeajacket')
    user.save()
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Amsterdam',
    )
    event = Event.objects.create(
        cult=cult,
        title='Westworld marathon',
        slug='westworld-marathon',
        details='Season 2 coming!',
        date='2018-02-02',
        time='18:00',
        venue='OK!Thess',
        address='Komotinis 2, 553 77',
        maps_url='https://goo.gl/maps/sample-link',
    )
    Membership.objects.create(
        user=user,
        cult=cult,
        role=Membership.MEMBER,
    )
    Attendance.objects.create(
        user=user,
        event=event,
    )
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    assert logged_in
    assert Attendance.objects.filter().count() == 1
    response = c.post('/attendance/' + cult.slug + '/' + event.slug + '/delete/', {})
    assert response.status_code == 302
    assert Attendance.objects.filter().count() == 0
