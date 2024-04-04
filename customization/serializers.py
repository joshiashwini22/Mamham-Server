# serializers.py

from rest_framework import serializers

from authentication.serializers import CustomerSerializer, AddressSerializer
from .models import CustomOrder, Dish, DishList
from drf_writable_nested.serializers import WritableNestedModelSerializer


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'


class DishListSerializer(serializers.ModelSerializer):
    dish = serializers.PrimaryKeyRelatedField(queryset=Dish.objects.all())

    class Meta:
        model = DishList
        fields = ['id', 'dish', 'quantity']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['dish'] = DishSerializer(instance.dish).data

        return representation


class CustomOrderSerializer(WritableNestedModelSerializer):
    dish_lists = DishListSerializer(many=True, required=False)

    class Meta:
        model = CustomOrder
        fields = ['id', 'dish_lists', 'customer', 'delivery_address', 'delivery_date', 'delivery_time', 'total',
                  'remarks', 'status', 'payment_method', 'isPaid', 'online_payment_response']


class CustomOrderDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    delivery_address = AddressSerializer(read_only=True)

    class Meta:
        model = CustomOrder
        fields = '__all__'