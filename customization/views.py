from rest_framework import viewsets

from .models import CustomOrder, DishList, Dish
from customization.serializers import CustomOrderSerializer, DishListSerializer, DishSerializer


class CustomOrderViewSet(viewsets.ModelViewSet):
    queryset = CustomOrder.objects.all()
    serializer_class = CustomOrderSerializer


class DishListViewSet(viewsets.ModelViewSet):
    queryset = DishList.objects.all()
    serializer_class = DishListSerializer


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    
