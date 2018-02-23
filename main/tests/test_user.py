import pytest
from django.test import Client

from main.forms import EmailForm, UserForm
from main.models import Cult, Membership, Profile


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


@pytest.mark.django_db()
def test_profile_not_found():
    c = Client()
    response = c.get('/@non_existent_user/')
    assert response.status_code == 404


@pytest.mark.django_db()
def test_edit_profile_not_found():
    c = Client()
    response = c.get('/@non_existent_user/edit/')
    assert response.status_code == 404


def test_get_login():
    c = Client()
    response = c.get('/login/')
    assert response.status_code == 200


@pytest.mark.django_db()
def test_email_form(django_user_model):
    user = django_user_model.objects.create(username='mother')
    user.set_password('takeajacket')
    user.save()
    form_data = {
        'email': 'daddy@cool.com',
    }
    form = EmailForm(data=form_data)
    assert form.is_valid()
    c = Client()
    response = c.post('/auth/', form_data)
    assert response.status_code == 302
    response = c.get('/login/')
    assert response.status_code == 200
    assert b'Login email sent! Please check your inbox and click on the link.' in response.content


@pytest.mark.django_db()
def test_logout(django_user_model):
    user = django_user_model.objects.create(username='mother')
    user.set_password('takeajacket')
    user.save()
    form_data = {
        'email': 'daddy@cool.com',
    }
    form = EmailForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    assert logged_in
    response = c.get('/logout/', follow=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.content


@pytest.mark.django_db()
def test_edit_user(django_user_model):
    user = django_user_model.objects.create(username='mother')
    user.set_password('takeajacket')
    user.profile.about = 'Built a wall.'
    user.save()
    form_data = {
        'username': 'daddycool',
        'about': 'Watching Grease',
    }
    form = UserForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    assert logged_in
    response = c.post('/@' + user.username + '/edit/', form_data, follow=True)
    assert response.status_code == 200
    assert b'Profile updated' in response.content
    assert form_data['username'].encode() in response.content
    assert form_data['about'].encode() in response.content


@pytest.mark.django_db()
def test_edit_other_user(django_user_model):
    user_1 = django_user_model.objects.create(username='mother')
    user_1.set_password('takeajacket')
    user_1.profile.about = 'Built a wall.'
    user_1.save()
    user_2 = django_user_model.objects.create(username='father')
    form_data = {
        'username': 'daddycool',
        'about': 'Watching Grease',
    }
    form = UserForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    assert logged_in
    response = c.post('/@' + user_2.username + '/edit/', form_data, follow=True)
    assert response.status_code == 403
