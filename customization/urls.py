from django.urls import path, include
from customization.views import CustomOrderViewSet, DishListViewSet, DishViewSet, DishByCategoryAPIView, \
    OrderByCustomer, CompletedOrderByCustomer, OngoingOrderByCustomer, CustomOrderListViewSet, OrderDashboardAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'custom-order', CustomOrderViewSet, basename='custom order')
router.register(r'get-custom-order', CustomOrderListViewSet, basename='custom order list')
router.register(r'dish-list', DishListViewSet, basename='dish list')
router.register(r'dishes', DishViewSet, basename='dishes')

urlpatterns = [
    path('', include(router.urls)),
    path('dishes/category/<str:category>/', DishByCategoryAPIView.as_view(), name='dishes-by-category'),
    path('myorders/by-customer/<int:customer_id>/', OrderByCustomer.as_view(), name='orders-by-customer'),
    path('completed-orders/<int:customer_id>/<str:status_type>/', CompletedOrderByCustomer.as_view(), name='completed-orders'),
    path('ongoing-orders/<int:customer_id>/ongoing/', OngoingOrderByCustomer.as_view(), name='ongoing-orders'),
    path('dashboard/order', OrderDashboardAPIView.as_view(), name='dashboard-order'),

]
