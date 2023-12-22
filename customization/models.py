from django.db import models
from authentication.models import Customer, Address


# Create your models here.
class CustomOrder(models.Model):
    status_choices = (
        ("Pending", 'Pending'),
        ("Approved", 'Approved'),
        ("Getting Ready", 'Getting Ready'),
        ("On the Way", 'On the Way'),
        ("Completed", 'Completed')
    )
    customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)
    delivery_address = models.ForeignKey(Address, null=True, on_delete=models.CASCADE)
    delivery_time = models.DateTimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=20, choices=status_choices, default='Pending')

    class Meta:
        verbose_name = "Custom Order"
        verbose_name_plural = "Custom Orders"


class Dish(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField()
    description = models.TextField()


class DishList(models.Model):
    customer = models.ForeignKey(CustomOrder, null=True, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField()
