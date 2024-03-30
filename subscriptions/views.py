from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import Plan, Meal, Subscription, WeeklyMenu, SubscriptionDeliveryDetails, AddOn
from .serializers import PlanSerializer, MealSerializer, SubscriptionSerializer, WeeklyMenuSerializer, SubscriptionDeliveryDetailsSerializer, AddOnSerializer

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    # permission_classes = [IsAdminUser]  # Only admin can view and modify plans

class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    # permission_classes = [IsAdminUser]  # Only admin can view and modify meals

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    # permission_classes = [IsAuthenticated]  # Only authenticated users can view and modify subscriptions


class WeeklyMenuViewSet(viewsets.ModelViewSet):
    queryset = WeeklyMenu.objects.all()
    serializer_class = WeeklyMenuSerializer

    def get_queryset(self):
        queryset = self.queryset

        week_start_date = self.request.query_params.get('week_start_date')
        week_end_date = self.request.query_params.get('week_end_date')
        plan_id = self.request.query_params.get('plan_id')
        meals = self.request.query_params.get('meals')

        # Apply filtering if filter parameters are provided
        if week_start_date:
            queryset = queryset.filter(week_start_date=week_start_date)
        if week_end_date:
            queryset = queryset.filter(week_end_date=week_end_date)
        if plan_id:
            queryset = queryset.filter(plan__id=plan_id)  # Assuming plan is a ForeignKey
        if meals:
            queryset = queryset.filter(meals__id=meals)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Create the WeeklyMenu instance
            instance = serializer.save()

            # Get meal ids from request data
            meal_ids = request.data.get('meals', [])
            for meal_id in meal_ids:
                try:
                    meal = Meal.objects.get(pk=meal_id)
                    instance.meals.add(meal)  # Add meal to the WeeklyMenu
                except Meal.DoesNotExist:
                    # Handle the case where meal with given id does not exist
                    pass

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionDeliveryDetailsViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionDeliveryDetails.objects.all()
    serializer_class = SubscriptionDeliveryDetailsSerializer
    # permission_classes = [IsAuthenticated]  # Only authenticated users can view and modify delivery details

class AddOnViewSet(viewsets.ModelViewSet):
    queryset = AddOn.objects.all()
    serializer_class = AddOnSerializer