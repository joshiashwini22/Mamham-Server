from rest_framework import serializers
from .models import CustomOrder, DishList, Dish


class DishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DishList
        fields = '__all__'


class CustomOrderSerializer(serializers.ModelSerializer):
    details = DishListSerializer(many=True, read_only=True)

    class Meta:
        model = CustomOrder
        fields = '__all__'


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'
