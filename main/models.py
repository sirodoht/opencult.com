from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Cult(models.Model):
    members = models.ManyToManyField(User, through='Membership')
    name = models.CharField(max_length=100)
    doctrine = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    cult = models.ForeignKey(Cult, on_delete=models.CASCADE)
    attendees = models.ManyToManyField(User, through='Attendance')
    title = models.CharField(max_length=100)
    details = models.TextField(blank=True, null=True)
    when = models.DateTimeField(default=timezone.now)
    venue = models.TextField()

    def __str__(self):
        return self.title


class Membership(models.Model):
    cult = models.ForeignKey(Cult, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(default=timezone.now)

    ADMIN = 'admin'
    MEMBER = 'member'
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (MEMBER, 'Member'),
    )
    role = models.CharField(
        choices=ROLE_CHOICES,
        max_length=50,
        default=MEMBER,
    )

    def __str__(self):
        return self.cult.name + ' :: ' + self.user.username


class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_rsvped = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.event.user + ' :: ' + self.user.username
