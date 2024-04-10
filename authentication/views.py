import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.serializers import UserSerializer, CustomerSerializer, AddressSerializer, UserLoginSerializer, NotificationSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from authentication.models import Customer, User, Address, Notification
import requests

from subscriptions.models import Subscription
from .emails import *
import random


def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


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

        otp = generate_otp()

        customerSerializer = CustomerSerializer(data={
            **request.data,
            "user": user_obj.id,
            "otp": otp
        })
        customerSerializer.is_valid(raise_exception=True)
        customer_obj = customerSerializer.save()
        print(user_obj.email)
        send_otp_via_mail(user_obj.email, otp)
        return Response(userSerializer.data, status=status.HTTP_201_CREATED)


class VerifyEmail(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp_entered = request.data.get('otp')

        try:
            customer = Customer.objects.get(user__email=email)
            if customer.otp == otp_entered:
                customer.is_verified = True
                customer.save()
                return Response({"message": "Email verified successfully."}, status=200)
            else:
                return Response({"error": "Invalid OTP."}, status=400)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=404)


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

            # Check if the email is verified
            try:
                customer = Customer.objects.get(user=user)
                if not customer.is_verified:
                    return Response({'message': 'Email is not verified.'}, status=400)
            except Customer.DoesNotExist:
                pass
    else:
        return Response({'message': 'Please provide valid credentials.'}, status=400)

    user = authenticate(**login_data)

    if not user:
        return Response({'message': 'Invalid credentials.'}, status=400)

    user.lastLogin = datetime.datetime.now()
    user.save()
    token = TokenObtainPairSerializer.get_token(user)


    serialized_user = UserLoginSerializer(user).data

    # Construct response
    response_data = {
        'message': 'Log in successful',
        'token': {
            'access': str(token.access_token),
            'refresh': str(token),
            'userinfo': UserLoginSerializer(user).data
        }
    }

    # Set token in Authorization header
    response = Response(response_data, status=200)
    response['Authorization'] = f'Bearer {response_data}'
    return response


@api_view(['POST'])
def refresh_token(request):
    if 'refresh' not in request.data:
        return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

    refresh = request.data['refresh']
    try:
        refresh_token = RefreshToken(refresh)
        access_token = str(refresh_token.access_token)
        # Check if the refresh token is expired
        if refresh_token.is_expired:
            return Response({'error': 'Refresh token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Generate a new access token and return it
            new_access_token = str(refresh_token.access_token)
            return Response({'access_token': new_access_token}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        user = request.user
        if user.is_authenticated:
            logout(request)
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response({'message': 'User is not authenticated'}, status=status.HTTP_400_BAD_REQUEST)


def get_addresses_for_customer(request, customer_id):
    try:
        # Retrieve all addresses for the given customer ID
        addresses = Address.objects.filter(customer_id=customer_id)
        # Serialize addresses data if needed
        addresses_data = [{'id': address.id, 'label': address.label, 'address_line1': address.address_line1, 'city': address.city} for
                          address in addresses]
        return JsonResponse({'addresses': addresses_data}, status=200)
    except Address.DoesNotExist:
        # Handle the case where no addresses are found for the customer
        return JsonResponse({'error': 'No addresses found for the customer'}, status=404)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


@api_view(['GET'])
def user_notifications(request, user_id):
    try:
        notifications = Notification.objects.filter(user=user_id).order_by('-id')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    except Notification.DoesNotExist:
        return Response({'error': 'No notifications'}, status=status.HTTP_404_NOT_FOUND)



def initiate_khalti_payment(request, order):
    if isinstance(order,Subscription):
        purchase_id=f'SUB-{order.id}'
    else:
        purchase_id=f'CO-{order.id}'

    # Here you would call the Khalti API to initiate the payment
    url = 'https://a.khalti.com/api/v2/epayment/initiate/'
    total_amount = float(order.total) * 100  # Multiply by 100 to convert to paisa
    return_url = request.build_absolute_uri(reverse('authentication:verify-payment'))
    payload = json.dumps({
        "return_url": return_url,
        "website_url": "http://localhost:3000/",
        "amount": total_amount,
        "purchase_order_id": purchase_id,
        "purchase_order_name": "test",
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
        order.save()
        return response.json()
    else:
        return {'error': 'Failed to initiate Khalti payment'}


def verifyKhalti(request):
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    if request.method == 'GET':
        headers = {
            'Authorization': 'key 8b05a1003bea4fc189b0058548a25857',
            'Content-Type': 'application/json',
        }
        pidx = request.GET.get('pidx')
        data = json.dumps({
            'pidx': pidx
        })
        res = requests.request('POST', url, headers=headers, data=data)
        print(res)
        print(res.text)

        new_res = json.loads(res.text)
        print(new_res)

        if new_res['status'] == 'Completed':
            # user = request.user
            # user.has_verified_dairy = True
            # user.save()
            # perform your db interaction logic
            pass

        # else:
        #     # give user a proper error message
        #     raise BadRequest("sorry ")

        return redirect('http://localhost:3000/')