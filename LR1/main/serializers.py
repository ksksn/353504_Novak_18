from rest_framework import serializers
from .models import (
    Service, ServiceType, Order, Client, Contract, Device, Part, Review,
    Employee, DeviceType, PartType
)

class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    service_type_name = serializers.CharField(source='service_type.name', read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'service_type', 'service_type_name', 'is_active', 'created_at']

class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    device_type_name = serializers.CharField(source='device_type.name', read_only=True)
    client_name = serializers.CharField(source='client.user.get_full_name', read_only=True)
    
    class Meta:
        model = Device
        fields = ['id', 'name', 'device_type', 'device_type_name', 'model', 'serial_number', 'client', 'client_name']

class PartTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartType
        fields = '__all__'

class PartSerializer(serializers.ModelSerializer):
    part_type_name = serializers.CharField(source='part_type.name', read_only=True)
    
    class Meta:
        model = Part
        fields = ['id', 'name', 'part_type', 'part_type_name', 'price', 'in_stock']

class ClientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Client
        fields = ['id', 'username', 'full_name', 'email', 'phone', 'address', 'birth_date', 'is_vip', 'registration_date']

class EmployeeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'username', 'full_name', 'position', 'phone', 'email', 'hire_date']

class ContractSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.user.get_full_name', read_only=True)
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    
    class Meta:
        model = Contract
        fields = ['id', 'number', 'client', 'client_name', 'employee', 'employee_name', 
                 'date_signed', 'deadline', 'total_sum', 'is_completed', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    contract_number = serializers.CharField(source='contract.number', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'contract', 'contract_number', 'service', 'service_name', 
                 'device', 'device_name', 'quantity', 'service_sum', 'parts_sum', 
                 'total_sum', 'status', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.user.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'client', 'client_name', 'rating', 'text', 'is_moderated', 'created_at']
        read_only_fields = ['client', 'is_moderated']
