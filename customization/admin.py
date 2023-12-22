from django.contrib import admin
from customization.models import CustomOrder, DishList, Dish
# Register your models here.

admin.site.register(
    [CustomOrder, DishList, Dish])