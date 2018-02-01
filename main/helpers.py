import shortuuid
from django.contrib.auth.models import User


def generate_username(email):
    username = email.split('@')[0]

    # check if exists
    if User.objects.filter(username=username).count():
        uuid = shortuuid.ShortUUID('abdcefghkmnpqrstuvwxyzABDCEFGHKMNPQRSTUVWXYZ23456789').random(length=12)
        username += uuid

    return username
