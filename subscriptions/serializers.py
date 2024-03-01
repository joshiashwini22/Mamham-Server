from rest_framework import serializers
from .models import Plan, Meal, AddOn, Subscription, WeeklyMenu, SubscriptionDeliveryDetails


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'description', 'price', 'image']


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'name', 'description', 'image']


class AddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOn
        fields = ['id', 'name', 'description', 'image', 'price']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'customer', 'start_date', 'duration', 'delivery_address', 'status', 'dietary_goal', 'meal_type', 'addons', 'remarks', 'plan']


class WeeklyMenuSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model = WeeklyMenu
        fields = ['id', 'week_start_date', 'week_end_date', 'plan', 'meals']


class SubscriptionDeliveryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionDeliveryDetails
        fields = ['id', 'subscription', 'customer', 'delivery_address', 'delivery_date', 'delivery_time', 'status']
