from django.db import models
from authentication.models import Customer, Address


class CustomOrder(models.Model):
    status_choices = (
        ("Pending", 'Pending'),
        ("Approved", 'Approved'),
        ("Preparing", 'Preparing'),
        ("On the Way", 'On the Way'),
        ("Completed", 'Completed')
    )
    payment_choices = (
        ("Cash On Delivery", 'Cash On Delivery'),
        ("Khalti", 'Khalti'),
    )
    customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)
    delivery_address = models.ForeignKey(Address, null=True, on_delete=models.CASCADE)
    delivery_date = models.DateField(null=True)
    delivery_time = models.TimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=status_choices, default='Pending')
    payment_method = models.CharField(max_length=20, choices=payment_choices, default='Cash On Delivery', null=True)
    isPaid = models.BooleanField(default=False, null=True)
    online_payment_response = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Custom Order"
        verbose_name_plural = "Custom Orders"

    def __str__(self):
        return str(self.id)

class Dish(models.Model):
    category_choices = (
        ("Base", 'Base'),
        ("Lentil", 'Lentil'),
        ("Veggie", 'Veggie'),
        ("Protein", 'Protein'),
        ("Pickle", 'Pickle')
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="dish_images", blank=True, null=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=category_choices, default='Base')
    isAvailable = models.BooleanField(default=True, null=True)


    class Meta:
        verbose_name = "Dish"
        verbose_name_plural = "Dishes"

    def __str__(self):
        return self.name


class DishList(models.Model):
    order = models.ForeignKey(CustomOrder, related_name="dish_lists", null=True, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        verbose_name = "Dish List"
        verbose_name_plural = "Dish Lists"

    def __str__(self):
        return str(self.order)  # Convert to string to return the order ID




