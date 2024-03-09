# serializers.py

from rest_framework import serializers
from .models import CustomOrder, Dish, DishList

class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'

class DishListSerializer(serializers.ModelSerializer):
    dish = DishSerializer()

    class Meta:
        model = DishList
        fields = ['dish', 'quantity']

class CustomOrderSerializer(serializers.ModelSerializer):
    dish_lists = DishListSerializer(many=True, required=False)

    class Meta:
        model = CustomOrder
        fields = '__all__'

    def create(self, validated_data):
        dish_lists_data = validated_data.pop('dish_lists', [])
        order = CustomOrder.objects.create(**validated_data)
        for dish_list_data in dish_lists_data:
            DishList.objects.create(order=order, **dish_list_data)
        return order
