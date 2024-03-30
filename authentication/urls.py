from django.urls import path, include
from . import views
from authentication.views import CustomerViewSet, UserViewSet, AddressViewSet, initiate_khalti_payment
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'user', UserViewSet, basename='user')
router.register(r'address', AddressViewSet, basename='address')

urlpatterns = [
    path('register/', views.RegisterUser.as_view(), name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('initiatekhalti/', views.initiate_khalti_payment, name='initiate'),
    path('', include(router.urls)),

]

