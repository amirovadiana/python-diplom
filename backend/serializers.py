from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter,
    Order, OrdeItem, Contact
)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id']

    def create(self, validated_data):        
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'url', 'accept_orders']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id']


class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = '__all__'
        read_only_fields = ['id']


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = '__all__'
        read_only_fields = ['id']


class ProductParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductParameter
        fields = '__all__'
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id']


class OrdeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdeItem
        fields = '__all__'
        read_only_fields = ['id']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['id']
