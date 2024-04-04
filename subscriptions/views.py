from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.views import initiate_khalti_payment
from .models import Plan, Meal, Subscription, WeeklyMenu, SubscriptionDeliveryDetails, AddOn
from .serializers import PlanSerializer, MealSerializer, SubscriptionSerializer, WeeklyMenuSerializer, SubscriptionDeliveryDetailsSerializer, AddOnSerializer
from customization.pagination import StandardResultsSetPagination

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the order
            self.perform_create(serializer)

            # Process payment based on the selected method
            print("Khalti ho la")

                # Integrate with Khalti API to initiate payment
            khalti_response = initiate_khalti_payment(request, serializer.instance)
            if khalti_response.get('success', True):
                   # Payment initiated successfully, update order status
                serializer.instance.paid = True
                serializer.instance.online_payment_response = khalti_response
                serializer.instance.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                    # Payment initiation failed
                return Response({'error': 'Failed to initiate Khalti payment'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class AddOnViewSet(viewsets.ModelViewSet):
    queryset = AddOn.objects.all()
    serializer_class = AddOnSerializer


class SubscriptionByCustomer(APIView):
    def get(self, request, customer_id):
        orders = Subscription.objects.filter(customer=customer_id)
        serializer = SubscriptionSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompletedSubscriptionByCustomer(APIView):
    def get(self, request, customer_id, status_type):

        if status_type == 'completed':
            orders = Subscription.objects.filter(customer=customer_id, status='COMPLETED')
        else:
            return Response({'error': 'Invalid status type'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SubscriptionSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OngoingSubscriptionByCustomer(APIView):
    def get(self, request, customer_id):
        orders = Subscription.objects.filter(customer=customer_id).exclude(status='COMPLETED')
        serializer = SubscriptionSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)