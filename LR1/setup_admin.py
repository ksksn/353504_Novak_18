#!/usr/bin/env python
"""
Скрипт для создания суперпользователя и наполнения базы данных тестовыми данными
"""
import os
import sys

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
    
    # Создание категорий
    categories = [
        {'name': 'Ремонт смартфонов', 'description': 'Ремонт мобильных устройств'},
        {'name': 'Ремонт планшетов', 'description': 'Ремонт планшетных компьютеров'},
        {'name': 'Ремонт ноутбуков', 'description': 'Ремонт портативных компьютеров'},
    ]
    
    for cat_data in categories:
        Category.objects.get_or_create(**cat_data)
    
    # Создание типов устройств
    device_types = [
        {'name': 'Смартфон', 'description': 'Мобильные телефоны'},
        {'name': 'Планшет', 'description': 'Планшетные компьютеры'},
        {'name': 'Ноутбук', 'description': 'Портативные компьютеры'},
    ]
    
    for dt_data in device_types:
        DeviceType.objects.get_or_create(**dt_data)
    
    # Создание типов запчастей
    part_types = [
        {'name': 'Экран', 'description': 'Дисплеи и тачскрины'},
        {'name': 'Батарея', 'description': 'Аккумуляторы'},
        {'name': 'Материнская плата', 'description': 'Основные платы'},
        {'name': 'Камера', 'description': 'Модули камер'},
    ]
    
    for pt_data in part_types:
        PartType.objects.get_or_create(**pt_data)
    
    # Создание специализаций сотрудников
    specializations = [
        {'name': 'Ремонт смартфонов', 'description': 'Специалист по ремонту мобильных устройств'},
        {'name': 'Ремонт ноутбуков', 'description': 'Специалист по ремонту ноутбуков'},
        {'name': 'Диагностика', 'description': 'Диагностика неисправностей'},
    ]
    
    for spec_data in specializations:
        EmployeeSpecialization.objects.get_or_create(**spec_data)
    
    # Создание типов услуг
    service_types = [
        {'name': 'Замена экрана', 'description': 'Замена дисплея'},
        {'name': 'Замена батареи', 'description': 'Замена аккумулятора'},
        {'name': 'Диагностика', 'description': 'Проверка устройства'},
        {'name': 'Чистка', 'description': 'Очистка от пыли и грязи'},
    ]
    
    for st_data in service_types:
        ServiceType.objects.get_or_create(**st_data)
    
    # Создание услуг
    services_data = [
        {'name': 'Замена экрана iPhone', 'price': Decimal('150.00'), 'service_type': ServiceType.objects.get(name='Замена экрана')},
        {'name': 'Замена батареи iPhone', 'price': Decimal('80.00'), 'service_type': ServiceType.objects.get(name='Замена батареи')},
        {'name': 'Диагностика устройства', 'price': Decimal('25.00'), 'service_type': ServiceType.objects.get(name='Диагностика')},
        {'name': 'Чистка ноутбука', 'price': Decimal('60.00'), 'service_type': ServiceType.objects.get(name='Чистка')},
    ]
    
    for service_data in services_data:
        Service.objects.get_or_create(
            name=service_data['name'],
            defaults={
                'description': f"Услуга: {service_data['name']}",
                'price': service_data['price'],
                'service_type': service_data['service_type']
            }
        )
    
    # Создание запчастей
    parts_data = [
        {'name': 'Экран iPhone 12', 'part_type': PartType.objects.get(name='Экран'), 'price': Decimal('120.00'), 'in_stock': 10},
        {'name': 'Батарея iPhone 12', 'part_type': PartType.objects.get(name='Батарея'), 'price': Decimal('50.00'), 'in_stock': 15},
        {'name': 'Экран Samsung Galaxy', 'part_type': PartType.objects.get(name='Экран'), 'price': Decimal('100.00'), 'in_stock': 8},
        {'name': 'Батарея MacBook', 'part_type': PartType.objects.get(name='Батарея'), 'price': Decimal('200.00'), 'in_stock': 3},
    ]
    
    for part_data in parts_data:
        Part.objects.get_or_create(**part_data)
    
    # Создание SparePart (дополнительных запчастей)
    spare_parts_data = [
        {'name': 'Экран iPhone 13', 'category': 'Дисплеи', 'price': Decimal('140.00'), 'quantity_in_stock': 12},
        {'name': 'Тачскрин Samsung', 'category': 'Дисплеи', 'price': Decimal('90.00'), 'quantity_in_stock': 7},
        {'name': 'Аккумулятор Samsung', 'category': 'Батареи', 'price': Decimal('45.00'), 'quantity_in_stock': 20},
        {'name': 'Камера iPhone', 'category': 'Камеры', 'price': Decimal('80.00'), 'quantity_in_stock': 5},
    ]
    
    for spare_data in spare_parts_data:
        SparePart.objects.get_or_create(**spare_data)
    
    # Создание тестовых пользователей-клиентов
    users_data = [
        {'username': 'client1', 'first_name': 'Иван', 'last_name': 'Петров', 'email': 'ivan@example.com'},
        {'username': 'client2', 'first_name': 'Мария', 'last_name': 'Сидорова', 'email': 'maria@example.com'},
        {'username': 'client3', 'first_name': 'Алексей', 'last_name': 'Козлов', 'email': 'alex@example.com'},
    ]
    
    for user_data in users_data:
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(
                password='password123',
                **user_data
            )
            
            # Создание паспортных данных
            passport = PassportData.objects.create(
                series='HB',
                number=f'123456{user.id}',
                issued_by='РОВД г. Минска',
                issue_date=date(2015, 1, 1)
            )
            
            # Создание клиента
            Client.objects.get_or_create(
                user=user,
                defaults={
                    'phone': f'+375 (29) 123-45-{user.id:02d}',
                    'address': f'ул. Примерная, {user.id}',
                    'birth_date': date(1990, 1, 1),
                    'passport': passport,
                    'is_vip': user.id == 1
                }
            )
    
    # Создание тестовых сотрудников
    emp_users_data = [
        {'username': 'master1', 'first_name': 'Сергей', 'last_name': 'Мастер', 'email': 'master1@example.com'},
        {'username': 'manager1', 'first_name': 'Ольга', 'last_name': 'Менеджер', 'email': 'manager1@example.com'},
    ]
    
    for emp_data in emp_users_data:
        if not User.objects.filter(username=emp_data['username']).exists():
            user = User.objects.create_user(
                password='password123',
                **emp_data
            )
            
            position = 'master' if 'master' in user.username else 'manager'
            
            Employee.objects.get_or_create(
                user=user,
                defaults={
                    'position': position,
                    'description': f'Опытный {position}',
                    'phone': f'+375 (29) 987-65-{user.id:02d}',
                    'email': user.email,
                    'birth_date': date(1985, 1, 1),
                    'hire_date': date(2020, 1, 1),
                    'salary': Decimal('1500.00') if position == 'master' else Decimal('1200.00')
                }
            )
    
    # Создание устройств для клиентов
    clients = Client.objects.all()[:3]
    device_types_list = list(DeviceType.objects.all())
    
    devices_data = [
        {'name': 'iPhone 12', 'model': 'A2172', 'serial_number': 'F17ABC123456'},
        {'name': 'Samsung Galaxy S21', 'model': 'SM-G991B', 'serial_number': 'R58DEF789012'},
        {'name': 'MacBook Pro', 'model': 'A2338', 'serial_number': 'C02GHI345678'},
    ]
    
    for i, device_data in enumerate(devices_data):
        if clients:
            Device.objects.get_or_create(
                serial_number=device_data['serial_number'],
                defaults={
                    'name': device_data['name'],
                    'device_type': device_types_list[i % len(device_types_list)],
                    'model': device_data['model'],
                    'client': clients[i % len(clients)]
                }
            )
    
    print("Тестовые данные созданы")

def main():
    print("Создание суперпользователя и тестовых данных...")
    admin_user = create_superuser()
    create_test_data()
    print("\n" + "="*50)
    print("НАСТРОЙКА ЗАВЕРШЕНА!")
    print("="*50)
    print("Логин: admin")
    print("Пароль: admin")
    print("URL админки: http://localhost:8000/admin/")
    print("="*50)

if __name__ == '__main__':
    main()
