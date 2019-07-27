from background_task import background
from django.core.mail import send_mail


@background(schedule=1)
def email_async(subject, body, from_email, receiver_emails):
    send_mail(subject, body, from_email, receiver_emails)
