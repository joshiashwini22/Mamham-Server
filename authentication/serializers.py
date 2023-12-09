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

    # def create(self, validated_data):
    #     user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
    #     return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    phoneNumber = serializers.CharField()
    address = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ('user', 'phoneNumber', 'address')
