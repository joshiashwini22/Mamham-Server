from django.urls import path
from . import views
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

urlpatterns = [
    path('api/register/', views.RegisterUser.as_view(), name='signup'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/login/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]