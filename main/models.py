from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(blank=True, null=True)

    @property
    def leader_of_list(self):
        return self.user.cult_set.filter(membership__role=Membership.LEADER)

    @property
    def member_of_count(self):
        return self.user.cult_set.filter(membership__role=Membership.MEMBER).count()

    @property
    def member_of_list(self):
        return self.user.cult_set.filter(membership__role=Membership.MEMBER)

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
    slug = models.CharField(max_length=100, unique=True)
    doctrine = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)

    @property
    def leaders_count(self):
        return self.members.filter(membership__role=Membership.LEADER).count()

    @property
    def leaders_list(self):
        return self.members.filter(membership__role=Membership.LEADER)

    @property
    def members_count(self):
        return self.members.count()

    @property
    def members_list(self):
        return self.members.filter(membership__role=Membership.MEMBER)

    def __str__(self):
        return self.name


class Event(models.Model):
    cult = models.ForeignKey(Cult, on_delete=models.CASCADE)
    attendees = models.ManyToManyField(User, through='Attendance')
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    details = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    venue = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100)
    maps_url = models.URLField(blank=True, null=True)

    @property
    def attendees_count(self):
        return self.attendees.count()

    @property
    def attendees_list(self):
        return self.attendees.order_by('attendance__date_rsvped')

    def __str__(self):
        return self.title


class Membership(models.Model):
    cult = models.ForeignKey(Cult, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(default=timezone.now)

    LEADER = 'leader'
    MEMBER = 'member'
    ROLE_CHOICES = (
        (LEADER, 'Leader'),
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
        return self.user.username + ' :: ' + self.event.title
