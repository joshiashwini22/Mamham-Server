from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Address(models.Model):
    label = models.CharField(max_length=50, default='Location')
    address_line1 = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    latitude = models.FloatField()  # Changed from IntegerField
    longitude = models.FloatField()  # Changed from IntegerField
    customer = models.ForeignKey(Customer, related_name='addresses', on_delete=models.CASCADE)


class Notification(models.Model):
    user = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)


