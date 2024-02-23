from django.urls import path, include
from subscriptions.views import PlanViewSet, WeeklyMenuViewSet, SubscriptionViewSet, MealViewSet, SubscriptionDeliveryDetailsViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'plans', PlanViewSet)
router.register(r'meals', MealViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'weekly-menu', WeeklyMenuViewSet)
router.register(r'subscription-delivery-details', SubscriptionDeliveryDetailsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
