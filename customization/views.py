from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView

from authentication.models import Notification, Customer
from .models import CustomOrder, DishList, Dish
from customization.serializers import CustomOrderSerializer, DishListSerializer, DishSerializer, \
    CustomOrderDetailSerializer
import requests
from authentication.views import initiate_khalti_payment
from customization.pagination import StandardResultsSetPagination


class CustomOrderViewSet(viewsets.ModelViewSet):
    queryset = CustomOrder.objects.all()
    serializer_class = CustomOrderSerializer
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the order
            self.perform_create(serializer)

            # Create a notification for the admin
            staff_users = User.objects.filter(is_staff=True)

            # Assuming you want to notify all staff users, you can iterate over them
            for staff_user in staff_users:
                message = f"A new order has been placed, (ID: #{serializer.instance.id})"
                # Create notification for each staff user
                Notification.objects.create(user=staff_user, message=message, created_at=timezone.now())


            customermessage = f"Thank you for ordering! Your order has been placed. (Order ID: #{serializer.instance.id})"
            customer = serializer.validated_data.get('customer')
            # Create a notification for the customer
            receivercustomer = Customer.objects.get(id=customer.id)
            userreceiver = receivercustomer.user
            Notification.objects.create(user=userreceiver, message=customermessage, created_at=timezone.now())

            # Process payment based on the selected method
            payment_method = serializer.validated_data.get('payment_method')

            if payment_method == 'Khalti':
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
            else:
                # For Cash On Delivery
                serializer.instance.payment_method = 'Cash On Delivery'
                serializer.instance.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():

            # Save the updated order
            self.perform_update(serializer)

            receiverupdate = Customer.objects.get(id=instance.customer.id)
            userreceiverupdate = receiverupdate.user_id
            print(userreceiverupdate)

            message = f"Your order status for Order ID: #{serializer.instance.id} is {serializer.instance.status}"
            Notification.objects.create(user_id=userreceiverupdate, message=message)

            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #
    # def initiate_khalti_payment(self, order):
    #     # Here you would call the Khalti API to initiate the payment
    #     url = 'https://khalti.com/api/v2/epayment/initiate/'
    #     total_amount = float(order.total) * 100  # Multiply by 100 to convert to paisa
    #
    #     payload =  json.dumps({
    #         "return_url": "http://google.com/",
    #         "website_url": "http://localhost:3000/",
    #         "amount": total_amount,
    #         "purchase_order_id": order.id,
    #         "purchase_order_name": "test",
    #         "customer_info": {
    #             "name": "Ram Bahadur",
    #             "email": "test@khalti.com",
    #             "phone": "9800000001"
    #         }
    #     })
    #     print(payload)
    #     headers = {
    #         'Authorization': 'Key test_secret_key_5327491a91ff4f688544e72de574e9f5',
    #         'Content-Type': 'application/json',
    #     }
    #
    #     response = requests.post(url, json=payload, headers=headers)
    #
    #     if response.status_code == 200:
    #         order.isPaid = True
    #         return response.json()
    #     else:
    #         return {'error': 'Failed to initiate Khalti payment'}


class CustomOrderListViewSet(viewsets.ModelViewSet):
    queryset = CustomOrder.objects.all()
    serializer_class = CustomOrderDetailSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        # Retrieve filter parameters from query parameters
        delivery_date = self.request.query_params.get('delivery_date')
        delivery_time = self.request.query_params.get('delivery_time')
        status = self.request.query_params.get('status')
        order_id = self.request.query_params.get('order_id')

        # Apply filtering if filter parameters are provided
        if delivery_date:
            queryset = queryset.filter(delivery_date=delivery_date)
        if delivery_time:
            queryset = queryset.filter(delivery_time=delivery_time)
        if status:
            queryset = queryset.filter(status=status)
        if order_id:
            queryset = queryset.filter(id=order_id)

        # Order by creation date in descending order (latest orders first)
        queryset = queryset.order_by('-id')

        return queryset


class DishListViewSet(viewsets.ModelViewSet):
    queryset = DishList.objects.all()
    serializer_class = DishListSerializer


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer


class DishByCategoryAPIView(APIView):
    def get(self, request, category):
        # Filter dishes by category
        dishes = Dish.objects.filter(category=category)
        serializer = DishSerializer(dishes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderByCustomer(APIView):
    def get(self, request, customer_id):
        orders = CustomOrder.objects.filter(customer=customer_id)
        serializer = CustomOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompletedOrderByCustomer(APIView):
    def get(self, request, customer_id, status_type):

        if status_type == 'completed':
            orders = CustomOrder.objects.filter(customer=customer_id, status='Completed')
        else:
            return Response({'error': 'Invalid status type'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CustomOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OngoingOrderByCustomer(APIView):
    def get(self, request, customer_id):
        orders = CustomOrder.objects.filter(customer=customer_id).exclude(status='Completed')
        serializer = CustomOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
