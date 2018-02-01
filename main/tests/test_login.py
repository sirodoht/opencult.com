import pytest
from django.test import Client

from main.forms import EmailForm


def test_email_form(django_user_model):
    c = Client()
    response = c.post('/login/')
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
