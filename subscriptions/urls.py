from django.urls import path, include
from subscriptions.views import PlanViewSet, WeeklyMenuViewSet, SubscriptionViewSet, MealViewSet, \
    SubscriptionDeliveryDetailsViewSet, AddOnViewSet, SubscriptionByCustomer, OngoingSubscriptionByCustomer, \
    CompletedSubscriptionByCustomer, SubscriptionListViewSet, DeliveryListViewSet, CustomerDeliveryListViewSet, \
    SubscriptionDashboardAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'meals', MealViewSet, basename='meal')
router.register(r'addons', AddOnViewSet, basename='addon')
router.register(r'subscription-order', SubscriptionViewSet, basename='subscription')
router.register(r'weekly-menu', WeeklyMenuViewSet, basename='weekly-menu')
router.register(r'subscription-delivery-details', SubscriptionDeliveryDetailsViewSet, basename='subscription-delivery-details')
router.register(r'get-subscription-order', SubscriptionListViewSet, basename='subscription order list')
router.register(r'subscription-deliveries', DeliveryListViewSet, basename='subscription-deliveries-by-date')


urlpatterns = [
    path('', include(router.urls)),
    path('mysubscriptions/by-customer/', SubscriptionByCustomer.as_view(), name='subscriptions-by-customer'),
    path('completed-subscriptions/<int:customer_id>/<str:status_type>/', CompletedSubscriptionByCustomer.as_view(),
         name='completed-subscriptions'),
    path('ongoing-subscriptions/<int:customer_id>/ongoing/', OngoingSubscriptionByCustomer.as_view(), name='ongoing-subscriptions'),
    path('customer-deliveries/<int:customer_id>/<int:subscription_id>/', CustomerDeliveryListViewSet.as_view(),
         name='customer-deliveries'),
    path('dashboard/subscriptionlist/', SubscriptionDashboardAPIView.as_view(), name='dashboard-subscription'),
]


