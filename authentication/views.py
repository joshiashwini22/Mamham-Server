import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.tokens import RefreshToken

from authentication.serializers import UserSerializer, CustomerSerializer, AddressSerializer, UserLoginSerializer, \
    NotificationSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from authentication.models import Customer, User, Address, Notification, AdminUser
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


class ResendOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            customer = Customer.objects.get(user__email=email)
            otp = generate_otp()  # Generate a new OTP
            customer.otp = otp
            customer.save()
            send_otp_via_mail(email, otp)
            return Response({"message": "OTP resent successfully."}, status=200)
        except ObjectDoesNotExist:
            return Response({"error": "Customer not found."}, status=404)


class ForgotPassword(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            if email == "admin@mail.com":
                admin = AdminUser.objects.get(user__email=email)
                otp = generate_otp()  # Generate a new OTP
                admin.otp = otp
                admin.save()
                send_otp_admin_password__mail(otp)
                return Response({"message": "OTP for admin password"}, status=200)

            else:
                customer = Customer.objects.get(user__email=email)
                otp = generate_otp()  # Generate a new OTP
                customer.otp = otp
                customer.save()
                send_otp_forgot_password__mail(email, otp)
                return Response({"message": "OTP for forgot password"}, status=200)
        except ObjectDoesNotExist:
            return Response({"error": "Customer not found."}, status=404)


class ResetPassword(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp_entered = request.data.get('otp')
        new_password = request.data.get('new_password')

        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)

            if email == "admin@mail.com":
                # Retrieve the corresponding customer profile
                admin = AdminUser.objects.get(user=user)
                if admin.otp == otp_entered:
                    # Set the new password for the user
                    user.set_password(new_password)
                    user.save()
                    # Clear the OTP from the customer profile
                    admin.otp = None
                    admin.save()
                    return Response({"message": "Password reset for admin successful."}, status=200)
                else:
                    return Response({"error": "Invalid OTP."}, status=400)
            else:
                # Retrieve the corresponding customer profile
                customer = Customer.objects.get(user=user)

                # Check if the entered OTP matches the one saved in the customer profile
                if customer.otp == otp_entered:
                    # Set the new password for the user
                    user.set_password(new_password)
                    user.save()
                    # Clear the OTP from the customer profile
                    customer.otp = None
                    customer.save()
                    return Response({"message": "Password reset successfully."}, status=200)
                else:
                    return Response({"error": "Invalid OTP."}, status=400)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        except Customer.DoesNotExist:
            return Response({"error": "Customer profile not found."}, status=404)


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
    refresh = RefreshToken.for_user(user)
    # print(refresh)

    serialized_user = UserLoginSerializer(user).data

    # Construct response
    response_data = {
        'message': 'Log in successful',
        'token': {
            'access': str(token.access_token),
            'refresh': str(refresh),
            'userinfo': UserLoginSerializer(user).data
        }
    }
    print(response_data)
    # Set token in Authorization header
    response = Response(response_data, status=200)
    response['Authorization'] = f'Bearer {token.access_token}'
    return response


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
        addresses_data = [
            {'id': address.id, 'label': address.label, 'address_line1': address.address_line1, 'city': address.city} for
            address in addresses]
        return JsonResponse({'addresses': addresses_data}, status=200)
    except Address.DoesNotExist:
        # Handle the case where no addresses are found for the customer
        return JsonResponse({'error': 'No addresses found for the customer'}, status=404)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class AdminNotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def create(self, request, *args, **kwargs):
        # Retrieve the list of user IDs and the message from the request data
        user_ids = request.data.get('users', [])
        message = request.data.get('message', '')
        title = request.data.get('title', '')
        print(user_ids)

        # Check if user IDs or message are missing
        if not user_ids:
            return Response({'error': 'User IDs are required'}, status=status.HTTP_400_BAD_REQUEST)
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        created_notifications = []
        errors = []

        # Iterate over the list of user IDs
        for user_id in user_ids:
            try:
                print(user_id)
                # Retrieve the User instance corresponding to the user ID
                user_instance = User.objects.get(pk=user_id)
                # Create a Notification object for the user instance
                Notification.objects.create(user=user_instance, message=message)
                print(title, user_instance.email, message)
                send_notification_mail(title, user_instance.email, message)
            except Exception as e:
                # Collect any errors that occur during creation
                errors.append({'user_id': user_id, 'error': str(e)})

        # If any errors occurred during creation, return a Response with error details
        if errors:
            error_messages = [f"Error for user {error['user_id']}: {error['error']}" for error in errors]
            return Response({'errors': error_messages}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'success': 'Notifications created successfully'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_notifications(request):
    try:
        print(request.user)
        notifications = Notification.objects.filter(user=request.user).order_by('-id')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    except Notification.DoesNotExist:
        return Response({'error': 'No notifications'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def admin_notification(request):
    try:
        print(request.user)
        notifications = Notification.objects.filter(user=request.user).order_by('-id')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    except Notification.DoesNotExist:
        return Response({'error': 'No notifications'}, status=status.HTTP_404_NOT_FOUND)


def initiate_khalti_payment(request, order):
    if isinstance(order, Subscription):
        purchase_id = f'SUB-{order.id}'
    else:
        purchase_id = f'CO-{order.id}'

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
            pass

        return redirect('http://localhost:3000/payment-completion/')
