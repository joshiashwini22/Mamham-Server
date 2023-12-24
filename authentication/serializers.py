from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from authentication.models import Customer, Address


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8, write_only=True)

    username = serializers.CharField(max_length=255, validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_staff')


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Customer
        fields = ('user', 'address', 'first_name', 'last_name', 'phone_number')
