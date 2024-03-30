from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from .models import CustomOrder, DishList, Dish
from customization.serializers import CustomOrderSerializer, DishListSerializer, DishSerializer
import requests
from authentication.views import initiate_khalti_payment


class CustomOrderViewSet(viewsets.ModelViewSet):
    queryset = CustomOrder.objects.all()
    serializer_class = CustomOrderSerializer

    def get_queryset(self):
        queryset = self.queryset
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

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the order
            self.perform_create(serializer)

            # Process payment based on the selected method
            payment_method = serializer.validated_data.get('payment_method')

            if payment_method == 'Khalti':
                print("Khalti ho la")

                # Integrate with Khalti API to initiate payment
                khalti_response = initiate_khalti_payment(serializer.instance)
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
