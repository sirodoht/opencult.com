import pytest
from django.test import Client

from main.forms import EditEventForm, EventForm
from main.models import Attendance, Cult, Event, Membership


@pytest.mark.django_db()
def test_event_not_found():
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Amsterdam',
    )
    c = Client()
    response = c.get('/' + cult.slug + '/non-existent-event/')
    assert response.status_code == 404


@pytest.mark.django_db()
def test_event_no_attendees():
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
    response = c.get('/' + cult.slug + '/' + event.slug + '/')
    assert response.status_code == 200
    assert cult.name.encode() in response.content
    assert cult.slug.encode() in response.content
    assert cult.city.encode() in response.content
    assert event.title.encode() in response.content
    assert event.venue.encode() in response.content
    assert event.address.encode() in response.content
    assert event.maps_url.encode() in response.content
    assert b'Attendees (0)' in response.content
    assert b'No one is attending yet.' in response.content


@pytest.mark.django_db()
def test_event_1_attendee(django_user_model):
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
    Attendance.objects.create(
        event=event,
        user=user,
    )
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.get('/' + cult.slug + '/' + event.slug + '/')
    assert logged_in
    assert response.status_code == 200
    assert user.username.encode() in response.content
    assert cult.name.encode() in response.content
    assert cult.slug.encode() in response.content
    assert cult.city.encode() in response.content
    assert event.title.encode() in response.content
    assert event.venue.encode() in response.content
    assert event.address.encode() in response.content
    assert event.maps_url.encode() in response.content
    assert b'Attendees (1)' in response.content


@pytest.mark.django_db()
def test_event_3_attendees(django_user_model):
    user_1 = django_user_model.objects.create(username='mother')
    user_2 = django_user_model.objects.create(username='baila')
    user_3 = django_user_model.objects.create(username='morena')
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
    Attendance.objects.create(
        event=event,
        user=user_1,
    )
    Attendance.objects.create(
        event=event,
        user=user_2,
    )
    Attendance.objects.create(
        event=event,
        user=user_3,
    )
    c = Client()
    response = c.get('/' + cult.slug + '/' + event.slug + '/')
    assert response.status_code == 200
    assert cult.name.encode() in response.content
    assert cult.slug.encode() in response.content
    assert cult.city.encode() in response.content
    assert event.title.encode() in response.content
    assert event.venue.encode() in response.content
    assert event.address.encode() in response.content
    assert event.maps_url.encode() in response.content
    assert b'Attendees (3)' in response.content
    assert user_1.username.encode() in response.content
    assert user_2.username.encode() in response.content
    assert user_3.username.encode() in response.content


@pytest.mark.django_db()
def test_event_form(django_user_model):
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
        cult=cult,
        user=user,
        role=Membership.LEADER,
    )
    form_data = {
        'title': 'Stayin alive',
        'details': 'Whether you are a brother or whether you are a mother',
        'date': '2018-02-02',
        'time': '19:00',
        'venue': 'Berghain',
        'address': '123 Nowehere Strasse',
        'maps_url': 'https://goo.gl/maps/here',
    }
    form = EventForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.post('/' + cult.slug + '/new/', form_data)
    assert logged_in
    assert response.status_code == 302
    assert Event.objects.first()
    assert Event.objects.first().title == form_data['title']
    assert Event.objects.first().details == form_data['details']
    assert Event.objects.first().date.strftime('%Y-%m-%d') == form_data['date']
    assert Event.objects.first().time.strftime('%H:%M') == form_data['time']
    assert Event.objects.first().venue == form_data['venue']
    assert Event.objects.first().address == form_data['address']
    assert Event.objects.first().maps_url == form_data['maps_url']


@pytest.mark.django_db()
def test_event_form_member(django_user_model):
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
        cult=cult,
        user=user,
        role=Membership.MEMBER,
    )
    form_data = {
        'title': 'Stayin alive',
        'details': 'Whether you are a brother or whether you are a mother',
        'date': '2018-02-02',
        'time': '19:00',
        'venue': 'Berghain',
        'address': '123 Nowehere Strasse',
        'maps_url': 'https://goo.gl/maps/here',
    }
    form = EventForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.post('/' + cult.slug + '/new/', form_data)
    assert logged_in
    assert response.status_code == 403


@pytest.mark.django_db()
def test_event_form_anon(django_user_model):
    user = django_user_model.objects.create(username='mother')
    user.set_password('takeajacket')
    user.save()
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Amsterdam',
    )
    form_data = {
        'title': 'Stayin alive',
        'details': 'Whether you are a brother or whether you are a mother',
        'date': '2018-02-02',
        'time': '19:00',
        'venue': 'Berghain',
        'address': '123 Nowehere Strasse',
        'maps_url': 'https://goo.gl/maps/here',
    }
    form = EventForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.post('/' + cult.slug + '/new/', form_data)
    assert logged_in
    assert response.status_code == 403


@pytest.mark.django_db()
def test_event_new_anon(django_user_model):
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Amsterdam',
    )
    form_data = {
        'title': 'Stayin alive',
        'details': 'Whether you are a brother or whether you are a mother',
        'date': '2018-02-02',
        'time': '19:00',
        'venue': 'Berghain',
        'address': '123 Nowehere Strasse',
        'maps_url': 'https://goo.gl/maps/here',
    }
    form = EventForm(data=form_data)
    assert form.is_valid()
    c = Client()
    response = c.get('/' + cult.slug + '/new/')
    assert response.status_code == 302


@pytest.mark.django_db()
def test_event_edit_anon():
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
    response = c.get('/' + cult.slug + '/' + event.slug + '/edit/')
    assert response.status_code == 302


@pytest.mark.django_db()
def test_event_get_edit_form_nonmember(django_user_model):
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
    response = c.get('/' + cult.slug + '/' + event.slug + '/edit/')
    assert logged_in
    assert response.status_code == 403


@pytest.mark.django_db()
def test_event_get_edit_form_member(django_user_model):
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
        cult=cult,
        user=user,
        role=Membership.MEMBER,
    )
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.get('/' + cult.slug + '/' + event.slug + '/edit/')
    assert logged_in
    assert response.status_code == 403


@pytest.mark.django_db()
def test_event_get_edit_form_leader(django_user_model):
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
        cult=cult,
        user=user,
        role=Membership.LEADER,
    )
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.get('/' + cult.slug + '/' + event.slug + '/edit/')
    assert logged_in
    assert response.status_code == 200


@pytest.mark.django_db()
def test_event_post_edit_form_nonmember(django_user_model):
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
    form_data = {
        'title': 'Atomic Blonde Screening',
        'slug': 'atomic-blonde-screening',
        'details': 'Charlize Theron as a spy.',
        'date': '2018-04-04',
        'time': '21:00',
        'venue': 'Coho',
        'address': 'Sofouli 4, 523 11',
        'maps_url': 'https://goo.gl/maps/coho-link',
    }
    form = EditEventForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.get('/' + cult.slug + '/' + event.slug + '/edit/')
    assert logged_in
    assert response.status_code == 403


@pytest.mark.django_db()
def test_event_post_edit_form_member(django_user_model):
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
        cult=cult,
        user=user,
        role=Membership.MEMBER,
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
    form_data = {
        'title': 'Atomic Blonde Screening',
        'slug': 'atomic-blonde-screening',
        'details': 'Charlize Theron as a spy.',
        'date': '2018-04-04',
        'time': '21:00',
        'venue': 'Coho',
        'address': 'Sofouli 4, 523 11',
        'maps_url': 'https://goo.gl/maps/coho-link',
    }
    form = EditEventForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.get('/' + cult.slug + '/' + event.slug + '/edit/')
    assert logged_in
    assert response.status_code == 403


@pytest.mark.django_db()
def test_event_post_edit_form_leader(django_user_model):
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
        cult=cult,
        user=user,
        role=Membership.LEADER,
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
    form_data = {
        'title': 'Atomic Blonde Screening',
        'slug': 'atomic-blonde-screening',
        'details': 'Charlize Theron as a spy.',
        'date': '2018-04-04',
        'time': '21:00',
        'venue': 'Coho',
        'address': 'Sofouli 4, 523 11',
        'maps_url': 'https://goo.gl/maps/coho-link',
    }
    form = EditEventForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    assert logged_in
    response = c.post('/' + cult.slug + '/' + event.slug + '/edit/', form_data, follow=True)
    assert response.status_code == 200
    assert form_data['title'].encode() in response.content
    assert form_data['slug'].encode() in response.content
    assert form_data['details'].encode() in response.content
    assert b'Wednesday, April 4, 2018 at 21:00 local time.' in response.content
    assert form_data['venue'].encode() in response.content
    assert form_data['address'].encode() in response.content
    assert form_data['maps_url'].encode() in response.content
