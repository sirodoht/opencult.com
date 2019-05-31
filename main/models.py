from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    about = models.TextField(blank=True, null=True)

    @property
    def leader_of_list(self):
        return self.group_set.filter(membership__role=Membership.LEADER)

    @property
    def member_of_count(self):
        return self.group_set.filter(membership__role=Membership.MEMBER).count()

    @property
    def member_of_list(self):
        return self.group_set.filter(membership__role=Membership.MEMBER)

    def __str__(self):
        return self.username


class Group(models.Model):
    members = models.ManyToManyField(CustomUser, through="Membership")
    name = models.CharField(max_length=100)
    date_created = models.DateTimeField(default=timezone.now)
    slug = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
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
        return self.members.filter()

    def __str__(self):
        return self.name


class Event(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    attendees = models.ManyToManyField(CustomUser, through="Attendance")
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True, db_index=True)
    details = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    venue = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    maps_url = models.URLField(blank=True, null=True)

    @property
    def attendees_count(self):
        return self.attendees.count()

    @property
    def attendees_list(self):
        return self.attendees.order_by("attendance__date_rsvped")

    def __str__(self):
        return self.title


class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(default=timezone.now)

    LEADER = "leader"
    MEMBER = "member"
    ROLE_CHOICES = ((LEADER, "Leader"), (MEMBER, "Member"))
    role = models.CharField(choices=ROLE_CHOICES, max_length=50, default=MEMBER)

    def __str__(self):
        return self.group.name + " :: " + self.user.username


class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_rsvped = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username + " :: " + self.event.title


class Comment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    body = models.TextField()

    class Meta:
        ordering = ["date_posted"]

    def __str__(self):
        return self.body[:50] + "(...)"
