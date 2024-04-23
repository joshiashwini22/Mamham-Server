from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.emails import send_subscription_email
from authentication.models import Customer, Notification
from authentication.views import initiate_khalti_payment
from .models import Plan, Meal, Subscription, WeeklyMenu, SubscriptionDeliveryDetails, AddOn
from .serializers import PlanSerializer, MealSerializer, SubscriptionSerializer, WeeklyMenuSerializer, \
    SubscriptionDeliveryDetailsSerializer, AddOnSerializer, DeliveryListSerializer, SubscriptionListSerializer
from customization.pagination import StandardResultsSetPagination
from django.db.models import Count
from django.db import models


class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all().order_by('-id')
    serializer_class = PlanSerializer


class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all().order_by('-id')
    serializer_class = MealSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    authentication_classes = [JWTAuthentication]

    def perform_update(self, serializer):
        instance = serializer.save()
        # Update related SubscriptionDeliveryDetails
        delivery_details = SubscriptionDeliveryDetails.objects.filter(subscription=instance)
        for detail in delivery_details:
            detail.delivery_address = instance.delivery_address
            detail.delivery_time = instance.delivery_time
            detail.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.user.is_staff)
        if serializer.is_valid():
            # Save the order
            self.perform_create(serializer)

            # Process payment based on the selected method
            print("Khalti ho la")

            # Integrate with Khalti API to initiate payment
            khalti_response = initiate_khalti_payment(request, serializer.instance)
            print(khalti_response)
            if khalti_response.get('success', True):
                # Payment initiated successfully, update order status
                serializer.instance.paid = True
                serializer.instance.online_payment_response = khalti_response
                serializer.instance.save()
                # Create SubscriptionDeliveryDetails objects
                subscription = serializer.instance
                delivery_dates = [subscription.start_date + timedelta(days=i) for i in
                                  range(int(subscription.duration[:-1]))]
                for delivery_date in delivery_dates:
                    SubscriptionDeliveryDetails.objects.create(
                        subscription=subscription,
                        delivery_address=subscription.delivery_address,
                        delivery_date=delivery_date,
                        delivery_time=subscription.delivery_time,
                        status='SCHEDULED'
                    )

                # Create a notification for the admin
                staff_users = User.objects.filter(is_staff=True)

                # Assuming you want to notify all staff users, you can iterate over them
                for staff_user in staff_users:
                    message = f"A new subscription has been placed, (ID: #{serializer.instance.id})"
                    # Create notification for each staff user
                    Notification.objects.create(user=staff_user, message=message, created_at=timezone.now())

                customermessage = f"Thank you for subscribing! Your order has been placed. Please check your email for details. (Subscription ID: #{serializer.instance.id})"
                Notification.objects.create(user=request.user, message=customermessage, created_at=timezone.now())

                send_subscription_email(request, subscription, request.user.email)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            else:
                # Payment initiation failed
                return Response({'error': 'Failed to initiate Khalti payment'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():

            self.perform_update(serializer)

            receiverupdate = Customer.objects.get(id=instance.customer.id)
            userreceiverupdate = receiverupdate.user_id
            print(userreceiverupdate)

            message = f"There were some changes. Your order status for Order ID: #{serializer.instance.id} is {serializer.instance.status}."
            Notification.objects.create(user_id=userreceiverupdate, message=message, created_at=timezone.now())

            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionListViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        customer = self.request.query_params.get('customer')
        start_date = self.request.query_params.get('start_date')
        delivery_time = self.request.query_params.get('delivery_time')
        status = self.request.query_params.get('status')

        if customer:
            queryset = queryset.filter(customer=customer)
        if start_date:
            queryset = queryset.filter(start_date=start_date)
        if delivery_time:
            queryset = queryset.filter(delivery_time=delivery_time)
        if status:
            queryset = queryset.filter(status=status)

        # Iterate over each subscription and update its status if the end date has passed
        for subscription in queryset:
            if subscription.end_date < timezone.now().date() and subscription.status != 'COMPLETED':
                subscription.status = 'COMPLETED'
                subscription.save()

        # Order by creation date in descending order (latest orders first)
        queryset = queryset.order_by('-id')

        return queryset


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

        queryset = queryset.order_by('-id')

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check if a WeeklyMenu with the same week_start_date already exists
            week_start_date = request.data.get("week_start_date")
            plan_id = request.data.get("plan")  # Assuming plan is passed in the request

            # Check for existing weekly menu with same start date and plan
            if WeeklyMenu.objects.filter(week_start_date=week_start_date, plan_id=plan_id).exists():
                return Response(
                    {"detail": "A WeeklyMenu with this start date already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
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

    def update(self, request, pk=None):
        instance = self.get_object()  # Get the instance to be updated
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            instance = serializer.save()  # Save any general data updates

            # Clear existing meal associations and add new ones
            meal_ids = request.data.get("meals", [])
            # Remove all existing meals
            instance.meals.clear()

            # Add new meals from the meal_ids list
            for meal_id in meal_ids:
                try:
                    meal = Meal.objects.get(pk=meal_id)
                    instance.meals.add(meal)
                except Meal.DoesNotExist:
                    pass

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class SubscriptionDeliveryDetailsViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionDeliveryDetails.objects.all()
    serializer_class = SubscriptionDeliveryDetailsSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            # Save the updated subscription delivery details
            self.perform_update(serializer)

            # Get the user receiving the notification
            user_receiver = instance.subscription.customer.user.id

            message = f"Delivery for Subscription Delivery ID: #{instance.id} has been updated. Your order status is {instance.status}"

            # Create a notification for the user
            Notification.objects.create(user_id=user_receiver, message=message, created_at=timezone.now())
            # Create a notification for the admin
            staff_users = User.objects.filter(is_staff=True)

            # Assuming you want to notify all staff users, you can iterate over them
            for staff_user in staff_users:
                message = f"Delivery changes have been made for, (ID: #{serializer.instance.id})"
                # Create notification for each staff user
                Notification.objects.create(user=staff_user, message=message, created_at=timezone.now())

            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddOnViewSet(viewsets.ModelViewSet):
    queryset = AddOn.objects.all().order_by('-id')
    serializer_class = AddOnSerializer


class SubscriptionByCustomer(APIView):
    def get(self, request, customer_id):
        orders = Subscription.objects.filter(customer=customer_id).order_by('-id')
        serializer = SubscriptionSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompletedSubscriptionByCustomer(APIView):
    def get(self, request, customer_id, status_type):

        if status_type == 'completed':
            orders = Subscription.objects.filter(customer=customer_id, status='COMPLETED').order_by('-id')
        else:
            return Response({'error': 'Invalid status type'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SubscriptionListSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OngoingSubscriptionByCustomer(APIView):
    def get(self, request, customer_id):
        # Retrieve ongoing subscriptions for the customer
        ongoing_subscriptions = Subscription.objects.filter(customer=customer_id, status='ONGOING').order_by('-id')

        # Iterate over each subscription and update its status if the end date has passed
        for subscription in ongoing_subscriptions:
            if subscription.end_date < timezone.now().date():
                subscription.status = 'COMPLETED'
                subscription.save()

        # Filter out completed subscriptions
        ongoing_subscriptions = ongoing_subscriptions.exclude(status='COMPLETED')

        # Serialize the ongoing subscriptions
        serializer = SubscriptionListSerializer(ongoing_subscriptions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DeliveryListViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionDeliveryDetails.objects.all()
    serializer_class = DeliveryListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        delivery_id = self.request.query_params.get('delivery_id')
        subscription = self.request.query_params.get('subscription')
        subscription__plan__id = self.request.query_params.get('subscription__plan__id')
        subscription__customer__id = self.request.query_params.get('subscription__customer__id')
        delivery_address = self.request.query_params.get('delivery_address')
        delivery_date = self.request.query_params.get('delivery_date')
        status = self.request.query_params.get('status')

        if subscription:
            queryset = queryset.filter(subscription=subscription)
        if delivery_address:
            queryset = queryset.filter(delivery_address=delivery_address)
        if delivery_date:
            queryset = queryset.filter(delivery_date=delivery_date)
        if status:
            queryset = queryset.filter(status=status)
        if delivery_id:
            queryset = queryset.filter(id=delivery_id)
        if subscription__plan__id:
            queryset = queryset.filter(subscription__plan__id=subscription__plan__id)
        if subscription__customer__id:
            queryset = queryset.filter(subscription__customer__id=subscription__customer__id)

        # Order by creation date in descending order (latest orders first)
        queryset = queryset.order_by('-id')

        return queryset


class CustomerDeliveryListViewSet(APIView):
    def get(self, request, customer_id, subscription_id):  # Add 'subscription_id' as a parameter
        deliveries = SubscriptionDeliveryDetails.objects.filter(subscription__customer=customer_id,
                                                                subscription_id=subscription_id).exclude(
            status='COMPLETED').order_by('-id')
        serializer = DeliveryListSerializer(deliveries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriptionDashboardAPIView(APIView):
    def get(self, request, format=None):
        # Total number of subscriptions
        total_subscriptions = Subscription.objects.count()

        # Number of subscriptions in each status
        subscription_status_counts = Subscription.objects.values('status').annotate(count=Count('id'))

        # Total revenue
        total_revenue = Subscription.objects.aggregate(total_revenue=models.Sum('total'))['total_revenue']

        subscription_status_counts_dict = {}
        for status_count in subscription_status_counts:
            subscription_status_counts_dict[status_count['status']] = status_count['count']

        # Response data
        data = {
            'total_subscriptions': total_subscriptions,
            'subscription_status_counts': subscription_status_counts_dict,
            'total_revenue': total_revenue}

        return Response(data)
