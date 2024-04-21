from django.core.mail import send_mail
from mamham_backend import settings


def send_otp_via_mail(email, otp):
    subject = "Account verification email"
    message = f"Your OTP for account verification is: {otp}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, email_from, recipient_list)


def send_otp_forgot_password__mail(email, otp):
    subject = "Password Reset"
    message = f"Your OTP for account verification is: {otp}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, email_from, recipient_list)


def send_otp_admin_password__mail(otp):
    subject = "Password Reset"
    message = f"Your OTP for account verification is: {otp}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['mamham.foods@gmail.com']

    send_mail(subject, message, email_from, recipient_list)


def send_notification_mail(title, email, message):
    subject = title
    message = message
    email_from = settings.EMAIL_HOST_USER  # Your email address
    recipient_list = [email]

    send_mail(subject, message, email_from, recipient_list)


def send_subscription_email(request, subscription, email):
    subject = 'Your Subscription Details'
    message = f"Hi {request.user},\n\n" \
                      f"Thank you for ordering from Mamham Foods " \
                      f"Here is you Subscription Details. " \
                      f"Subscription ID: {subscription.id}\n\n " \
                      f"Start Date: {subscription.start_date}\n\n " \
                      f"End Date: {subscription.end_date}\n\n " \
                      f"Delivery Time: {subscription.delivery_time}\n\n " \
                      f"Team Mamham"

    email_from = settings.EMAIL_HOST_USER  # Your email address
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    print(subject, message, email_from, recipient_list)
