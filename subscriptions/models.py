from django.db import models
from authentication.models import Customer, Address
from datetime import timedelta


class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="plan_images")


class Meal(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="meal_images")
    # category = models.CharField(max_length=100)


class AddOn(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="meal_images")
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Subscription(models.Model):
    DURATION_CHOICES = [
        ('7D', '7'),
        ('15D', '15'),
        ('30D', '30'),
    ]

    DIETARY_GOAL_CHOICES = [
        ('Regular', 'Regular Diet'),
        ('WeightLoss', 'Weight Loss'),
        ('Keto', 'Keto Meal'),
        ('MuscleGain', 'Gain Muscle'),
    ]

    MEAL_TYPE_CHOICES = [
        ('Veg', 'Vegetarian'),
        ('NonVeg', 'Non Vegetarian'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    duration = models.CharField(choices=DURATION_CHOICES, default='7D')
    delivery_address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    dietary_goal = models.CharField(max_length=20, choices=DIETARY_GOAL_CHOICES, default='Regular')
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPE_CHOICES, default='Veg')
    addons = models.ManyToManyField(AddOn, blank=True)
    remarks = models.TextField(blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)


class WeeklyMenu(models.Model):
    week_start_date = models.DateField()
    week_end_date = models.DateField()
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, default=1)
    meals = models.ManyToManyField(Meal, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new object
            # Assuming week_start_date is set before saving
            self.week_end_date = self.week_start_date + timedelta(days=6)  # Add 6 days for a week
        super().save(*args, **kwargs)


class SubscriptionDeliveryDetails(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    delivery_address = models.ForeignKey(Address, on_delete=models.CASCADE, default=1)
    delivery_date = models.DateField()
    delivery_time = models.TimeField()
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')

    def __str__(self):
        return f"{self.subscription} - {self.customer}"

    class Meta:
        verbose_name = "Subscription Delivery Details"
        verbose_name_plural = "Subscription Delivery Details"