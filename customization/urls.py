from django.urls import path, include
from customization.views import CustomOrderViewSet, DishListViewSet, DishViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'custom-order', CustomOrderViewSet, basename='custom order')
router.register(r'dish-list', DishListViewSet, basename='dish list')
router.register(r'dishes', DishViewSet, basename='dishes')

urlpatterns = [
    path('', include(router.urls))
]
