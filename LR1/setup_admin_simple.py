#!/usr/bin/env python
"""
Скрипт для создания суперпользователя и наполнения базы данных тестовыми данными
"""
import sys
import os

# Настройка Django ПЕРЕД импортами
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_website.settings')

import django
django.setup()

from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from decimal import Decimal

from main.models import (
    Client, Device, DeviceType, SparePart, PartType, Repair, RepairSparePart,
    Service, Employee, Order, Contract, ServiceType, EmployeeSpecialization
)

def create_superuser():
    """Создание суперпользователя admin/admin"""
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            password='admin',
            email='admin@example.com',
            first_name='Администратор',
            last_name='Системы'
        )
        print("✓ Создан суперпользователь: admin/admin")
        return admin_user
    else:
        print("✓ Суперпользователь уже существует")
        return User.objects.get(username='admin')

def create_test_data():
    """Создание тестовых данных"""
    
    # Создание типов устройств
    device_types = [
        {'name': 'Смартфон', 'description': 'Мобильный телефон'},
        {'name': 'Планшет', 'description': 'Планшетный компьютер'},
        {'name': 'Ноутбук', 'description': 'Портативный компьютер'},
        {'name': 'Телевизор', 'description': 'Телевизионный приемник'},
    ]
    
    for device_type_data in device_types:
        device_type, created = DeviceType.objects.get_or_create(
            name=device_type_data['name'],
            defaults={'description': device_type_data['description']}
        )
        if created:
            print(f"✓ Создан тип устройства: {device_type.name}")
    
    # Создание типов запчастей
    part_types = [
        {'name': 'Экран', 'description': 'Дисплейные модули'},
        {'name': 'Батарея', 'description': 'Аккумуляторные батареи'},
        {'name': 'Микросхема', 'description': 'Электронные компоненты'},
        {'name': 'Корпус', 'description': 'Корпусные детали'},
    ]
    
    for part_type_data in part_types:
        part_type, created = PartType.objects.get_or_create(
            name=part_type_data['name'],
            defaults={'description': part_type_data['description']}
        )
        if created:
            print(f"✓ Создан тип запчасти: {part_type.name}")
    
    # Создание типов услуг
    service_types = [
        {'name': 'Диагностика', 'description': 'Определение неисправности'},
        {'name': 'Замена экрана', 'description': 'Замена дисплейного модуля'},
        {'name': 'Замена батареи', 'description': 'Замена аккумулятора'},
        {'name': 'Чистка', 'description': 'Профилактическая чистка'},
    ]
    
    for service_type_data in service_types:
        service_type, created = ServiceType.objects.get_or_create(
            name=service_type_data['name'],
            defaults={'description': service_type_data['description']}
        )
        if created:
            print(f"✓ Создан тип услуги: {service_type.name}")
    
    # Создание специализаций сотрудников
    specializations = [
        {'name': 'Мобильные устройства', 'description': 'Ремонт смартфонов и планшетов'},
        {'name': 'Компьютеры', 'description': 'Ремонт ноутбуков и ПК'},
        {'name': 'Электроника', 'description': 'Ремонт бытовой электроники'},
    ]
    
    for spec_data in specializations:
        spec, created = EmployeeSpecialization.objects.get_or_create(
            name=spec_data['name'],
            defaults={'description': spec_data['description']}
        )
        if created:
            print(f"✓ Создана специализация: {spec.name}")
    
    # Создание тестового клиента
    test_user, created = User.objects.get_or_create(
        username='testclient',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Тестовый',
            'last_name': 'Клиент'
        }
    )
    if created:
        test_user.set_password('testpass')
        test_user.save()
    
    test_client, created = Client.objects.get_or_create(
        user=test_user,
        defaults={
            'phone': '+375 (29) 123-45-67',
            'address': 'г. Минск, ул. Тестовая, д. 1',
            'birth_date': '1990-01-01'
        }
    )
    if created:
        print(f"✓ Создан тестовый клиент: {test_client.user.get_full_name()}")
    
    # Создание устройств
    devices = [
        {
            'name': 'iPhone 13',
            'device_type': DeviceType.objects.get(name='Смартфон'),
            'model': 'iPhone 13',
            'serial_number': 'AP001',
            'client': test_client
        },
        {
            'name': 'Samsung Galaxy S21',
            'device_type': DeviceType.objects.get(name='Смартфон'),
            'model': 'Galaxy S21',
            'serial_number': 'SM001',
            'client': test_client
        },
        {
            'name': 'MacBook Pro',
            'device_type': DeviceType.objects.get(name='Ноутбук'),
            'model': 'MacBook Pro 13"',
            'serial_number': 'MB001',
            'client': test_client
        }
    ]
    
    for device_data in devices:
        device, created = Device.objects.get_or_create(
            serial_number=device_data['serial_number'],
            defaults=device_data
        )
        if created:
            print(f"✓ Создано устройство: {device.name}")
    
    # Создание запчастей
    spare_parts = [
        {
            'name': 'Экран iPhone 13',
            'category': 'Экран',
            'price': Decimal('12000.00'),
            'quantity_in_stock': 10,
        },
        {
            'name': 'Батарея Samsung S21',
            'category': 'Батарея',
            'price': Decimal('3500.00'),
            'quantity_in_stock': 5,
        },
        {
            'name': 'Клавиатура MacBook',
            'category': 'Корпус',
            'price': Decimal('8000.00'),
            'quantity_in_stock': 3,
        }
    ]
    
    for part_data in spare_parts:
        part, created = SparePart.objects.get_or_create(
            name=part_data['name'],
            defaults=part_data
        )
        if created:
            print(f"✓ Создана запчасть: {part.name}")
    
    # Создание услуг
    services = [
        {
            'name': 'Замена экрана iPhone',
            'type': ServiceType.objects.get(name='Замена экрана'),
            'price': Decimal('5000.00'),
            'duration_hours': 2,
            'description': 'Замена дисплея iPhone',
            'is_available': True
        },
        {
            'name': 'Диагностика смартфона',
            'type': ServiceType.objects.get(name='Диагностика'),
            'price': Decimal('1000.00'),
            'duration_hours': 1,
            'description': 'Полная диагностика смартфона',
            'is_available': True
        },
        {
            'name': 'Замена батареи',
            'type': ServiceType.objects.get(name='Замена батареи'),
            'price': Decimal('2500.00'),
            'duration_hours': 1,
            'description': 'Замена аккумулятора',
            'is_available': True
        }
    ]
    
    for service_data in services:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults=service_data
        )
        if created:
            print(f"✓ Создана услуга: {service.name}")
    
    print("✓ Тестовые данные созданы успешно!")

def main():
    """Главная функция"""
    print("=== Настройка админки ремонтного сервиса ===")
    print()
    
    # Создание суперпользователя
    admin_user = create_superuser()
    
    # Создание тестовых данных
    create_test_data()
    
    print()
    print("=== Настройка завершена ===")
    print("Для входа в админку используйте:")
    print("  Логин: admin")
    print("  Пароль: admin")
    print("  URL: http://127.0.0.1:8000/admin/")

if __name__ == '__main__':
    main()
