import random

from django.contrib.auth.models import User
from django.core.mail import send_mail

from authentication.models import Customer
from mamham_backend import settings


def send_otp_via_mail(email, otp):
    subject = "Account verification email"
    message = f"Your OTP for account verification is: {otp}"
    email_from = settings.EMAIL_HOST_USER  # Your email address
    recipient_list = [email]

    send_mail(subject, message, email_from, recipient_list)


def send_subscription_email(request, subscription, email):
    subject = 'Your Subscription Details'
    message = f"Hi {request.user},\n\n" \
                      f"Thank you for ordering from Mamham Foods " \
                      f"Here is you Subscription Details. " \
                      f"Subscription ID:\n\n{subscription.id}\n\n " \
                      f"Start Date:\n\n{subscription.start_date}\n\n " \
                      f"End Date:\n\n{subscription.end_date}\n\n " \
                      f"Delivery Time:\n\n{subscription.delivery_time}\n\n " \
                      f"Team Mamham"

    email_from = settings.EMAIL_HOST_USER  # Your email address
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    print(subject, message, email_from, recipient_list)
