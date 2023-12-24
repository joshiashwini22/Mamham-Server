from django.urls import path, include
from . import views
from authentication.views import CustomerViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')

urlpatterns = [
    path('register/', views.RegisterUser.as_view(), name='signup'),
    path('login/', views.login, name='login'),
    path('', include(router.urls))
]

