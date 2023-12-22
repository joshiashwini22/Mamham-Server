from django.db import models
from django.contrib.auth.models import User


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
    address_line2 = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    latitude = models.IntegerField()
    longitude = models.IntegerField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Payment(models.Model):
    CustomerID = models.ForeignKey(Customer, on_delete=models.CASCADE)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Method = models.CharField(max_length=255)
    Status = models.CharField(max_length=50)
    Type = models.CharField(max_length=50)  # 'Subscription' or 'CustomOrder'

