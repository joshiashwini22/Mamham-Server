from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Customer(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class AdminUser(models.Model):
    user = models.OneToOneField(User, related_name="adminuser", on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, unique=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "AdminUser"
        verbose_name_plural = "AdminUsers"


class Address(models.Model):
    label = models.CharField(max_length=50, default='Location')
    address_line1 = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, related_name='addresses', on_delete=models.CASCADE)


class Notification(models.Model):
    user = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)


