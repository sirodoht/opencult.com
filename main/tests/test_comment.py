import pytest
from django.test import Client

from main.forms import CommentForm
from main.models import Comment, Cult, Event, Membership


@pytest.mark.django_db()
def test_read_comment(django_user_model):
    user = django_user_model.objects.create(username='mother')
    user.set_password('takeajacket')
    user.save()
    cult = Cult.objects.create(
        name='SpaceX worshippers',
        slug='the-spacex-creed',
        doctrine='Mars, we\'re coming.',
        city='Los Angeles',
    )
    event = Event.objects.create(
        cult=cult,
        title='SpaceX Falcon Heavy launch',
        slug='falcon-heavy-launch',
        details='Mars! Incoming!',
        date='2118-02-02',
        time='18:00',
        venue='SpaceX Fans HQ',
        address='2314 Olympus Str, 553 77',
        maps_url='https://goo.gl/maps/sample-link',
    )
    comment = Comment.objects.create(
        author=user,
        event=event,
        body='Elon for president!',
    )
    c = Client()
    response = c.get('/' + cult.slug + '/' + event.slug + '/')
    assert response.status_code == 200
    assert comment.body.encode() in response.content


@pytest.mark.django_db()
def test_create_comment(django_user_model):
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
        title='SpaceX Falcon Heavy launch',
        slug='falcon-heavy-launch',
        details='Mars! Incoming!',
        date='2118-02-02',
        time='18:00',
        venue='SpaceX Fans HQ',
        address='2314 Olympus Str, 553 77',
        maps_url='https://goo.gl/maps/sample-link',
    )
    Membership.objects.create(
        cult=cult,
        user=user,
        role=Membership.LEADER,
    )
    form_data = {
        'body': 'Elon for president!',
    }
    form = CommentForm(data=form_data)
    assert form.is_valid()
    c = Client()
    logged_in = c.login(username='mother', password='takeajacket')
    response = c.post('/' + cult.slug + '/' + event.slug + '/comment/', form_data)
    assert logged_in
    assert response.status_code == 302
    assert Comment.objects.first()
    assert Comment.objects.first().body == form_data['body']
    assert Comment.objects.first().author == user
    assert Comment.objects.first().event == event
