import pytest
from django.test import Client

from main.models import Cult, Event, Membership
from main.forms import CultForm, EditCultForm


@pytest.mark.django_db()
def test_cult():
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
        maps_url='https://goo.gl/maps/sample=link',
    )
    c = Client()
    response = c.get('/' + cult.slug + '/')
    assert response.status_code == 200
    assert cult.name.encode() in response.content
    assert cult.slug.encode() in response.content
    assert cult.doctrine.encode() in response.content
    assert cult.city.encode() in response.content
    assert event.title.encode() in response.content
    assert event.slug.encode() in response.content
    assert event.venue.encode() in response.content
    assert event.address.encode() in response.content
    assert event.maps_url.encode() in response.content


@pytest.mark.django_db()
def test_cult_leader(django_user_model):
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
        maps_url='https://goo.gl/maps/sample=link',
    )
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.get('/' + cult.slug + '/')
    assert logged_in
    assert user.username.encode() in response.content
    assert response.status_code == 200
    assert cult.name.encode() in response.content
    assert cult.slug.encode() in response.content
    assert cult.doctrine.encode() in response.content
    assert cult.city.encode() in response.content
    assert event.title.encode() in response.content
    assert event.slug.encode() in response.content
    assert event.venue.encode() in response.content
    assert event.address.encode() in response.content
    assert event.maps_url.encode() in response.content
    assert b'Role' in response.content
    assert b'div class="section-body">Leader</div>' in response.content


@pytest.mark.django_db()
def test_cult_member(django_user_model):
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
        maps_url='https://goo.gl/maps/sample=link',
    )
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.get('/' + cult.slug + '/')
    assert logged_in
    assert user.username.encode() in response.content
    assert response.status_code == 200
    assert cult.name.encode() in response.content
    assert cult.slug.encode() in response.content
    assert cult.doctrine.encode() in response.content
    assert cult.city.encode() in response.content
    assert event.title.encode() in response.content
    assert event.slug.encode() in response.content
    assert event.venue.encode() in response.content
    assert event.address.encode() in response.content
    assert event.maps_url.encode() in response.content
    assert b'Role' in response.content
    assert b'div class="section-body">Member</div>' in response.content


@pytest.mark.django_db()
def test_cult_anon(django_user_model):
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
        maps_url='https://goo.gl/maps/sample=link',
    )
    c = Client()
    logged_in = c.login(username='mother', password='false_password')
    response = c.get('/' + cult.slug + '/')
    assert not logged_in
    assert response.status_code == 200
    assert b'login' in response.content
    assert user.username.encode() in response.content
    assert cult.name.encode() in response.content
    assert cult.slug.encode() in response.content
    assert cult.doctrine.encode() in response.content
    assert cult.city.encode() in response.content
    assert event.title.encode() in response.content
    assert event.slug.encode() in response.content
    assert event.venue.encode() in response.content
    assert event.address.encode() in response.content
    assert event.maps_url.encode() in response.content
    assert b'Role' not in response.content


@pytest.mark.django_db()
def test_cult_new_anon():
    c = Client()
    response = c.get('/new/')
    assert response.status_code == 302


@pytest.mark.django_db()
def test_cult_form(django_user_model):
    user = django_user_model.objects.create(username='mother')
    user.set_password('takeajacket')
    user.save()
    form_data = {
        'name': 'Turn around now',
        'doctrine': 'Did you think I\'d crumble?',
        'city': 'Berlin',
    }
    form = CultForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.post('/new/', form_data)
    assert logged_in
    assert response.status_code == 302
    assert Cult.objects.first()
    assert Cult.objects.first().name == form_data['name']
    assert Cult.objects.first().doctrine == form_data['doctrine']
    assert Cult.objects.first().city == form_data['city']


@pytest.mark.django_db()
def test_cult_edit_anon():
    cult = Cult.objects.create(
        name='Sweet Dreams',
        slug='sweet-dreams',
        doctrine='Hold your head up, keep your head up!',
        city='Amsterdam',
    )
    c = Client()
    response = c.get('/' + cult.slug + '/edit/')
    assert response.status_code == 302


@pytest.mark.django_db()
def test_cult_get_edit_form_nonmember(django_user_model):
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
    response = c.get('/' + cult.slug + '/edit/')
    assert logged_in
    assert response.status_code == 403


@pytest.mark.django_db()
def test_cult_get_edit_form_member(django_user_model):
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
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.get('/' + cult.slug + '/edit/')
    assert logged_in
    assert response.status_code == 403


@pytest.mark.django_db()
def test_cult_get_edit_form_leader(django_user_model):
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
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.get('/' + cult.slug + '/edit/')
    assert logged_in
    assert response.status_code == 200


@pytest.mark.django_db()
def test_cult_post_edit_form_nonmember(django_user_model):
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
        'name': 'Turn around now',
        'slug': 'pigs-on-the-wings',
        'doctrine': 'Did you think I\'d crumble?',
        'city': 'Berlin',
    }
    form = EditCultForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.post('/' + cult.slug + '/edit/', form_data)
    assert logged_in
    assert response.status_code == 403


@pytest.mark.django_db()
def test_cult_post_edit_form_member(django_user_model):
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
        'name': 'Turn around now',
        'slug': 'pigs-on-the-wings',
        'doctrine': 'Did you think I\'d crumble?',
        'city': 'Berlin',
    }
    form = EditCultForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.post('/' + cult.slug + '/edit/', form_data)
    assert logged_in
    assert response.status_code == 403


@pytest.mark.django_db()
def test_cult_post_edit_form_leader(django_user_model):
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
        'name': 'Turn around now',
        'slug': 'pigs-on-the-wings',
        'doctrine': 'Did you think I would crumble?',
        'city': 'Berlin',
    }
    form = EditCultForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    assert logged_in
    response = c.post('/' + cult.slug + '/edit/', form_data, follow=True)
    assert response.status_code == 200
    assert form_data['name'].encode() in response.content
    assert form_data['slug'].encode() in response.content
    assert form_data['doctrine'].encode() in response.content
    assert form_data['city'].encode() in response.content
