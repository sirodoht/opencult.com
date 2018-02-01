import pytest
from django.test import Client

from main.forms import EmailForm, UserForm


def test_get_login():
    c = Client()
    response = c.get('/login/')
    assert response.status_code == 200


def test_email_form():
    c = Client()
    response = c.post('/login/')
    assert response.status_code == 200


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
    assert b'You have been logged out.' in response.content


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
