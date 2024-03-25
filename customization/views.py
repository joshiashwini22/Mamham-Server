from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from .models import CustomOrder, DishList, Dish
from customization.serializers import CustomOrderSerializer, DishListSerializer, DishSerializer
import requests


class CustomOrderViewSet(viewsets.ModelViewSet):
    queryset = CustomOrder.objects.all()
    serializer_class = CustomOrderSerializer

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
                khalti_response = self.initiate_khalti_payment(serializer.instance)
                print(khalti_response)
                if khalti_response.get('success', True):
                    # Payment initiated successfully, update order status
                    serializer.instance.paid = True
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

    def initiate_khalti_payment(self, order):
        # Here you would call the Khalti API to initiate the payment
        url = 'https://khalti.com/api/v2/epayment/initiate/'
        total_amount = float(order.total) * 100  # Multiply by 100 to convert to paisa

        payload =  json.dumps({
            "return_url": "http://google.com/",
            "website_url": "http://localhost:3000/",
            "amount": total_amount,
            "purchase_order_id": order.id,
            "purchase_order_name": "test",
            "customer_info": {
                "name": "Ram Bahadur",
                "email": "test@khalti.com",
                "phone": "9800000001"
            }
        })
        print(payload)
        headers = {
            'Authorization': 'Key test_secret_key_5327491a91ff4f688544e72de574e9f5',
            'Content-Type': 'application/json',
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            order.isPaid = True
            return response.json()
        else:
            return {'error': 'Failed to initiate Khalti payment'}


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
    
