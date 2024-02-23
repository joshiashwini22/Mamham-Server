from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Plan, Meal, Subscription, WeeklyMenu, SubscriptionDeliveryDetails
from .serializers import PlanSerializer, MealSerializer, SubscriptionSerializer, WeeklyMenuSerializer, SubscriptionDeliveryDetailsSerializer

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAdminUser]  # Only admin can view and modify plans

class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    permission_classes = [IsAdminUser]  # Only admin can view and modify meals

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can view and modify subscriptions

class WeeklyMenuViewSet(viewsets.ModelViewSet):
    queryset = WeeklyMenu.objects.all()
    serializer_class = WeeklyMenuSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can view weekly menu

class SubscriptionDeliveryDetailsViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionDeliveryDetails.objects.all()
    serializer_class = SubscriptionDeliveryDetailsSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can view and modify delivery details
