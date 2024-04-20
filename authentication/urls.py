from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from authentication.views import CustomerViewSet, UserViewSet, AddressViewSet, initiate_khalti_payment, \
    get_addresses_for_customer, verifyKhalti, NotificationViewSet, user_notifications, admin_notification, VerifyEmail, AdminNotificationViewSet
from rest_framework.routers import DefaultRouter
app_name="authentication"

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'user', UserViewSet, basename='user')
router.register(r'address', AddressViewSet, basename='address')
router.register(r'notification-inbox', NotificationViewSet, basename='notification-inbox')
router.register(r'notification-create', AdminNotificationViewSet, basename='notification-create')

urlpatterns = [
    path('register/', views.RegisterUser.as_view(), name='signup'),
    path('verify-email/', views.VerifyEmail.as_view(), name='verify-email'),
    path('resend-otp/', views.ResendOTP.as_view(), name='resend-otp'),
    path('forgot-password/', views.ForgotPassword.as_view(), name='forgot-password'),
    path('reset-password/', views.ResetPassword.as_view(), name='reset-password'),
    path('login/', views.login, name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('initiatekhalti/', views.initiate_khalti_payment, name='initiate'),
    path('getaddressforcustomer/<int:customer_id>', views.get_addresses_for_customer, name='getaddressforcustomer'),
    path('verify-payment/', verifyKhalti, name='verify-payment'),
    path('', include(router.urls)),
    path('notification-user/', user_notifications, name='user-notifications'),
    path('notification-admin/', admin_notification, name='admin-notifications'),

]

