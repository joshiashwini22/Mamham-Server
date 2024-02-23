import datetime

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from authentication.serializers import UserSerializer, CustomerSerializer, AddressSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from authentication.models import Customer, Address



# Create your views here.
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


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
    if user.is_staff:
        serialized_user = UserSerializer(user).data
    else:
        customer = Customer.objects.get(user=user)
        serialized_user = CustomerSerializer(customer).data

    return Response({'message': 'Log in successful', 'token': {
        'access': str(token.access_token),
        'refresh': str(token),
        'user': serialized_user

    }}, status=200)


class LogoutView(APIView):
    def post(self, request):
        user = request.user
        if user.is_authenticated:
            logout(request)
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response({'message': 'User is not authenticated'}, status=status.HTTP_400_BAD_REQUEST)