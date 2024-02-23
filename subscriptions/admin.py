from django.contrib import admin
from subscriptions.models import Subscription, SubscriptionDeliveryDetails, Plan, Meal, WeeklyMenu
# Register your models here.

admin.site.register(
    [Subscription, SubscriptionDeliveryDetails, Plan, Meal, WeeklyMenu])