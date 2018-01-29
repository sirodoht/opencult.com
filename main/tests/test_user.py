import pytest
from django.test import Client

from main.models import Profile


def test_get_login():
    c = Client()
    response = c.get('/login/')
    assert response.status_code == 200
