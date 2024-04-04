from django.urls import path, include
from subscriptions.views import PlanViewSet, WeeklyMenuViewSet, SubscriptionViewSet, MealViewSet, SubscriptionDeliveryDetailsViewSet, AddOnViewSet, SubscriptionByCustomer, OngoingSubscriptionByCustomer, CompletedSubscriptionByCustomer
from rest_framework.routers import DefaultRouter
from authentication.views import verifyKhalti

router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'meals', MealViewSet, basename='meal')
router.register(r'addons', AddOnViewSet, basename='addon')
router.register(r'subscription-order', SubscriptionViewSet, basename='subscription')
router.register(r'weekly-menu', WeeklyMenuViewSet, basename='weekly-menu')
router.register(r'subscription-delivery-details', SubscriptionDeliveryDetailsViewSet, basename='subscription-delivery-details')

urlpatterns = [
    path('', include(router.urls)),
    path('mysubscriptions/by-customer/<int:customer_id>/', SubscriptionByCustomer.as_view(), name='subscriptions-by-customer'),
    path('completed-subscriptions/<int:customer_id>/<str:status_type>/', CompletedSubscriptionByCustomer.as_view(),
         name='completed-subscriptions'),
    path('ongoing-subscriptions/<int:customer_id>/ongoing/', OngoingSubscriptionByCustomer.as_view(), name='ongoing-subscriptions'),

]
