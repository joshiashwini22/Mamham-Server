from rest_framework import serializers
from .models import CustomOrder, OrderList, Dish


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderList
        fields = ('id', 'CustomOrderID', 'DishID', 'Quantity', 'ItemPrice')


class CustomOrderSerializer(serializers.ModelSerializer):
    details = OrderListSerializer(many=True, read_only=True)

    class Meta:
        model = CustomOrder
        fields = ('id', 'CustomerID', 'OrderDate', 'DeliveryTime', 'DeliveryAddress', 'Total', 'details')


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ('id', 'Name', 'Description', 'Price', 'Category', 'Image')
