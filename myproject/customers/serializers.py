from rest_framework import serializers
from .models import Customer

class ImportSerializer(serializers.Serializer):
    file = serializers.FileField()

class CreateCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone_number','date_of_birth','address']  # Replace with your model fields


