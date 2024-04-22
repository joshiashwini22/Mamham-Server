from django.db import models
from authentication.models import Customer, Address
from datetime import timedelta, time


class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="plan_images")

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Plans"

    def __str__(self):
        return self.name


class Meal(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="meal_images")

    class Meta:
        verbose_name = "Meal"
        verbose_name_plural = "Meals"

    def __str__(self):
        return self.name


class AddOn(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Add On"
        verbose_name_plural = "Add Ons"

    def __str__(self):
        return self.name


class Subscription(models.Model):
    DURATION_CHOICES = [
        ('7D', '7'),
        ('15D', '15'),
        ('30D', '30'),
    ]

    STATUS_CHOICES = [
        ('ONGOING', 'OnGoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    start_date = models.DateField()  # Set default value to current date
    end_date = models.DateField(null=True)  # Will be calculated based on start date and duration
    delivery_time = models.TimeField(default=time(10, 0))
    duration = models.CharField(choices=DURATION_CHOICES, default='7D', max_length=3)
    delivery_address = models.ForeignKey(Address, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ONGOING')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    addons = models.ManyToManyField(AddOn, blank=True)
    remarks = models.TextField(blank=True)
    isPaid = models.BooleanField(default=False)
    online_payment_response = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new object
            # Automatically set the end date based on start date and duration
            self.end_date = self.start_date + timedelta(days=int(self.duration[:-1]))
        super().save(*args, **kwargs)


class WeeklyMenu(models.Model):
    week_start_date = models.DateField()
    week_end_date = models.DateField()
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, default=1)
    meals = models.ManyToManyField(Meal, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new object
            # Week_start_date is set before saving
            self.week_end_date = self.week_start_date + timedelta(days=6)  # Add 6 days for a week
        super().save(*args, **kwargs)


class SubscriptionDeliveryDetails(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='delivery_details', null=True)
    delivery_address = models.ForeignKey(Address, on_delete=models.CASCADE)
    delivery_date = models.DateField()
    delivery_time = models.TimeField()
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('ONTHEWAY', 'On the Way'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')

    def __str__(self):
        return f"{self.subscription.customer} - {self.delivery_date} - {self.subscription}"

    class Meta:
        verbose_name = "Subscription Delivery Detail"
        verbose_name_plural = "Subscription Delivery Details"