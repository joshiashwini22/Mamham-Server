from rest_framework import serializers
from .models import Plan, Meal, AddOn, Subscription, WeeklyMenu, SubscriptionDeliveryDetails
from drf_writable_nested.serializers import WritableNestedModelSerializer


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
        fields = ['id', 'name', 'price']


class WeeklyMenuSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model = WeeklyMenu
        fields = ['id', 'week_start_date', 'week_end_date', 'plan', 'meals']


class SubscriptionDeliveryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionDeliveryDetails
        fields = ['id', 'subscription', 'delivery_address', 'delivery_date', 'delivery_time', 'status']


class SubscriptionSerializer(WritableNestedModelSerializer):
    delivery_details = SubscriptionDeliveryDetailsSerializer(many=True, required=False)

    class Meta:
        model = Subscription
        fields = ['id', 'customer', 'start_date', 'duration', 'delivery_address', 'delivery_time', 'total', 'status',
                  'addons', 'remarks', 'plan', 'delivery_details', 'isPaid', 'online_payment_response']
