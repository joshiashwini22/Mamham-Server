import datetime

from django.shortcuts import render
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from authentication.serializers import UserSerializer, CustomerSerializer, AddressSerializer, CustomerLoginSerializer, \
    UserLoginSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from authentication.models import Customer, User, Address
import requests


def initiate_khalti_payment(order):
    print("Khati Initiate")
    # Here you would call the Khalti API to initiate the payment
    url = 'https://a.khalti.com/api/v2/epayment/initiate/'
    # total_amount = float(order.total) * 100  # Multiply by 100 to convert to paisa

    payload = json.dumps({
        "return_url": "https://google.com/",
        "website_url": "http://localhost:3000/",
        "amount": 1300,
        "purchase_order_id": "test12",
        "purchase_order_name": "test",
        "customer_info": {
            "name": "Khalti Bahadur",
            "email": "example@gmail.com",
            "phone": "9800000123"
        },
        "amount_breakdown": [
            {
                "label": "Mark Price",
                "amount": 1000
            },
            {
                "label": "VAT",
                "amount": 300
            }
        ],
        "product_details": [
            {
                "identity": "1234567890",
                "name": "Khalti logo",
                "total_price": 1300,
                "quantity": 1,
                "unit_price": 1300
            }
        ]
    })
    print(payload)
    headers = {
        'Authorization': 'Key 8b05a1003bea4fc189b0058548a25857',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json())  # Directly parse response content as JSON
    if response.status_code == 200:
        order.isPaid = True
        return response.json()
    else:
        return {'error': 'Failed to initiate Khalti payment'}


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class RegisterUser(APIView):
    def post(self, request, format='json'):
        userSerializer = UserSerializer(data=request.data)
        userSerializer.is_valid(raise_exception=True)
        user_obj = userSerializer.save()
        customerSerializer = CustomerSerializer(data={
            **request.data,
            "user": user_obj.id
        })
        customerSerializer.is_valid(raise_exception=True)
        customer_obj = customerSerializer.save()
        return Response(userSerializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request: Request):
    login_data = {}

    if request.data.get('password'):
        login_data["password"] = request.data.get('password')

    else:
        return Response({'message': 'Please provide password.'}, status=400)

    if request.data.get('email'):
        if not User.objects.filter(email=request.data.get('email')).exists():
            return Response({'message': 'Provided credentials are invalid'}, status=400)
        else:
            user = User.objects.get(email=request.data.get('email'))
            login_data['username'] = user.username
    else:
        return Response({'message': 'Please provide valid credentials.'}, status=400)

    user = authenticate(**login_data)

    if not user:
        return Response({'message': 'Invalid credentials.'}, status=400)

    user.lastLogin = datetime.datetime.now()
    user.save()
    token = TokenObtainPairSerializer.get_token(user)
    # if user.is_staff:
    #     serialized_user = UserSerializer(user).data
    # else:
    #     customer = Customer.objects.get(user=user)
    #     serialized_user = CustomerLoginSerializer(customer).data

    serialized_user = UserLoginSerializer(user).data

    return Response({'message': 'Log in successful', 'token': {
        'access': str(token.access_token),
        'refresh': str(token),
        'userinfo': serialized_user

    }}, status=200)


class LogoutView(APIView):
    def post(self, request):
        user = request.user
        if user.is_authenticated:
            logout(request)
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response({'message': 'User is not authenticated'}, status=status.HTTP_400_BAD_REQUEST)
