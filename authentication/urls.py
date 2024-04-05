from django.urls import path, include
from . import views
from authentication.views import CustomerViewSet, UserViewSet, AddressViewSet, initiate_khalti_payment, get_addresses_for_customer, verifyKhalti, NotificationViewSet, user_notifications
from rest_framework.routers import DefaultRouter
app_name="authentication"

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'user', UserViewSet, basename='user')
router.register(r'address', AddressViewSet, basename='address')
router.register(r'notification-inbox', NotificationViewSet, basename='notification-inbox')

urlpatterns = [
    path('register/', views.RegisterUser.as_view(), name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('initiatekhalti/', views.initiate_khalti_payment, name='initiate'),
    path('getaddressforcustomer/<int:customer_id>', views.get_addresses_for_customer, name='getaddressforcustomer'),
    path('verify-payment/', verifyKhalti, name='verify-payment'),
    path('', include(router.urls)),
    path('notification-user/<int:user_id>/', user_notifications,
         name='user-notifications'),

]

