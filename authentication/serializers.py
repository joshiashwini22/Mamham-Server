from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from authentication.models import Customer, Address, Notification
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, required=False)  # Nested serializer for addresses
    otp = serializers.CharField(write_only=True)
    is_verified = serializers.BooleanField(default=False)
    class Meta:
        model = Customer
        fields = ('id', 'user', 'addresses', 'first_name', 'last_name', 'phone_number', 'otp', 'is_verified')


class CustomerLoginSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    addresses = AddressSerializer(many=True, required=False)  # Nested serializer for addresses

    class Meta:
        model = Customer
        fields = ('__all__')

    def to_representation(self, instance):
        # Get the authenticated user from the context
        authenticated_user = self.context['request'].user

        # Check if the instance user matches the authenticated user
        if instance.user == authenticated_user:
            # Filter addresses for the authenticated user
            addresses = instance.addresses.filter(user=authenticated_user)
            addresses_data = AddressSerializer(addresses, many=True).data
            instance.addresses = addresses_data
            return super().to_representation(instance)
        else:
            # If not, remove the addresses field from the representation
            data = super().to_representation(instance)
            data.pop('addresses', None)
            return data


class UserLoginSerializer(serializers.ModelSerializer):
    profile = CustomerSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff', 'profile')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'user_id', 'message', 'is_read')
