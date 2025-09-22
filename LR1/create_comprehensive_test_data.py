#!/usr/bin/env python
"""
Создание полноценных тестовых данных для демонстрации системы договоров
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_website.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import (
    Client, Employee, Service, ServiceType, Device, DeviceType, 
    SparePart, Contract, Order, PartType, Part, EmployeeSpecialization
)

def create_test_data():
    """Создание комплексных тестовых данных"""
    
    print("=== Создание тестовых данных для сервисного центра ===\n")
    
    service_types = [
        ("Диагностика", "Выявление неисправностей"),
        ("Ремонт", "Восстановление работоспособности"),
        ("Обслуживание", "Профилактические работы"),
        ("Настройка", "Конфигурирование устройств"),
        ("Замена комплектующих", "Установка новых деталей")
    ]
    
    print("Создаем типы услуг...")
    for name, desc in service_types:
        service_type, created = ServiceType.objects.get_or_create(
            name=name,
            defaults={'description': desc}
        )
        if created:
            print(f"✓ Создан тип услуги: {name}")
    
    services_data = [
        ("Диагностика компьютера", "Диагностика", 500.00),
        ("Диагностика ноутбука", "Диагностика", 450.00),
        ("Ремонт материнской платы", "Ремонт", 2500.00),
        ("Замена экрана ноутбука", "Замена комплектующих", 3500.00),
        ("Чистка от пыли", "Обслуживание", 800.00),
        ("Установка ОС", "Настройка", 1200.00),
        ("Восстановление данных", "Ремонт", 4000.00),
        ("Замена батареи ноутбука", "Замена комплектующих", 1800.00),
        ("Ремонт блока питания", "Ремонт", 1500.00),
        ("Настройка сети", "Настройка", 1000.00)
    ]
    
    print("\nСоздаем услуги...")
    for service_name, type_name, price in services_data:
        service_type = ServiceType.objects.get(name=type_name)
        service, created = Service.objects.get_or_create(
            name=service_name,
            defaults={
                'description': f'Качественный сервис: {service_name.lower()}',
                'price': Decimal(str(price)),
                'service_type': service_type,
                'is_active': True
            }
        )
        if created:
            print(f"✓ Создана услуга: {service_name} - {price} руб.")
    
    device_types = [
        ("Настольный компьютер", "Стационарные ПК"),
        ("Ноутбук", "Портативные компьютеры"),
        ("Планшет", "Планшетные компьютеры"),
        ("Смартфон", "Мобильные телефоны"),
        ("Принтер", "Печатающие устройства")
    ]
    
    print("\nСоздаем типы устройств...")
    for name, desc in device_types:
        device_type, created = DeviceType.objects.get_or_create(
            name=name,
            defaults={'description': desc}
        )
        if created:
            print(f"✓ Создан тип устройства: {name}")
    
    part_types = [
        ("Материнская плата", "Основные платы"),
        ("Процессор", "Центральные процессоры"),
        ("Оперативная память", "Модули RAM"),
        ("Жесткий диск", "Накопители данных"),
        ("Экран", "Дисплеи и матрицы"),
        ("Батарея", "Аккумуляторы"),
        ("Блок питания", "Источники питания")
    ]
    
    print("\nСоздаем виды запчастей...")
    for name, desc in part_types:
        part_type, created = PartType.objects.get_or_create(
            name=name,
            defaults={'description': desc}
        )
        if created:
            print(f"✓ Создан вид запчасти: {name}")
    
    parts_data = [
        ("Экран 15.6\" Full HD", "Экран", 4500.00, 5),
        ("Батарея для ноутбука 6-cell", "Батарея", 2800.00, 8),
        ("Материнская плата ASUS", "Материнская плата", 5500.00, 3),
        ("Процессор Intel Core i5", "Процессор", 8500.00, 2),
        ("RAM DDR4 8GB", "Оперативная память", 3200.00, 10),
        ("SSD 256GB", "Жесткий диск", 4200.00, 7),
        ("Блок питания 600W", "Блок питания", 2500.00, 4),
        ("Экран 13.3\" HD", "Экран", 3800.00, 6),
        ("Батарея для планшета", "Батарея", 1500.00, 12),
        ("HDD 1TB", "Жесткий диск", 2800.00, 9)
    ]
    
    print("\nСоздаем запчасти...")
    for part_name, type_name, price, stock in parts_data:
        part_type = PartType.objects.get(name=type_name)
        part, created = Part.objects.get_or_create(
            name=part_name,
            defaults={
                'part_type': part_type,
                'price': Decimal(str(price)),
                'in_stock': stock
            }
        )
        if created:
            print(f"✓ Создана запчасть: {part_name} - {price} руб. (в наличии: {stock})")
    
    print("\nСоздаем записи SparePart...")
    for part_name, type_name, price, stock in parts_data:
        spare_part, created = SparePart.objects.get_or_create(
            name=part_name,
            defaults={
                'category': type_name,
                'price': Decimal(str(price)),
                'quantity_in_stock': stock
            }
        )
        if created:
            print(f"✓ Создана SparePart: {part_name}")
    
    specializations = [
        ("Ремонт компьютеров", "Специализация на ремонте ПК"),
        ("Ремонт ноутбуков", "Специализация на ремонте ноутбуков"),
        ("Диагностика", "Выявление неисправностей"),
        ("Замена экранов", "Замена дисплеев"),
        ("Восстановление данных", "Работа с накопителями")
    ]
    
    print("\nСоздаем специализации...")
    for name, desc in specializations:
        spec, created = EmployeeSpecialization.objects.get_or_create(
            name=name,
            defaults={'description': desc}
        )
        if created:
            print(f"✓ Создана специализация: {name}")
    
    clients_data = [
        ("Иван", "Петров", "ivan.petrov@email.com", "+375291234567"),
        ("Мария", "Сидорова", "maria.sidorova@email.com", "+375291234568"),
        ("Андрей", "Козлов", "andrey.kozlov@email.com", "+375291234569"),
        ("Елена", "Волкова", "elena.volkova@email.com", "+375291234570"),
        ("Дмитрий", "Смирнов", "dmitry.smirnov@email.com", "+375291234571")
    ]
    
    print("\nСоздаем клиентов...")
    clients = []
    for first_name, last_name, email, phone in clients_data:
        username = f"{first_name.lower()}.{last_name.lower()}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': 'pbkdf2_sha256$600000$test$test'  # пароль: test
            }
        )
        
        if created:
            print(f"✓ Создан пользователь: {username}")
        
        client, created = Client.objects.get_or_create(
            user=user,
            defaults={
                'phone': phone,
                'address': f"г. Минск, ул. Тестовая, д. {len(clients)+1}",
                'birth_date': date(1990, 1, 1) + timedelta(days=len(clients)*365),
                'is_vip': len(clients) % 3 == 0  # Каждый третий - VIP
            }
        )
        
        if created:
            print(f"✓ Создан клиент: {first_name} {last_name}")
        
        clients.append(client)
    
    devices_data = [
        ("Asus VivoBook 15", "Ноутбук", "X515EA", "SN001234567"),
        ("HP Pavilion Desktop", "Настольный компьютер", "590-p0013w", "SN001234568"),
        ("MacBook Air", "Ноутбук", "M1 2021", "SN001234569"),
        ("iPhone 12", "Смартфон", "A2172", "SN001234570"),
        ("iPad Pro", "Планшет", "11-inch", "SN001234571"),
        ("Lenovo ThinkPad", "Ноутбук", "E15 Gen 2", "SN001234572"),
        ("Samsung Galaxy S21", "Смартфон", "SM-G991B", "SN001234573"),
        ("Dell Inspiron", "Настольный компьютер", "3880", "SN001234574"),
        ("HP LaserJet", "Принтер", "Pro M404n", "SN001234575"),
        ("Acer Aspire", "Ноутбук", "A315-23", "SN001234576")
    ]
    
    print("\nСоздаем устройства...")
    devices = []
    for i, (name, type_name, model, serial) in enumerate(devices_data):
        device_type = DeviceType.objects.get(name=type_name)
        client = clients[i % len(clients)]  # Распределяем устройства между клиентами
        
        device, created = Device.objects.get_or_create(
            name=name,
            client=client,
            defaults={
                'device_type': device_type,
                'model': model,
                'serial_number': serial
            }
        )
        
        if created:
            print(f"✓ Создано устройство: {name} для {client.user.get_full_name()}")
        
        devices.append(device)
    
    employees_data = [
        ("Петр", "Техник", "petr.technikov", "Старший мастер", "+375291111111", 2500.00),
        ("Анна", "Мастер", "anna.masterova", "Мастер", "+375291111112", 2000.00),
        ("Сергей", "Диагностик", "sergey.diagnostov", "Диагност", "+375291111113", 1800.00)
    ]
    
    print("\nСоздаем сотрудников...")
    employees = []
    for first_name, last_name, username, position, phone, salary in employees_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': f"{username}@company.com",
                'password': 'pbkdf2_sha256$600000$test$test',
                'is_staff': True
            }
        )
        
        if created:
            print(f"✓ Создан пользователь сотрудника: {username}")
        
        employee, created = Employee.objects.get_or_create(
            user=user,
            defaults={
                'position': position,
                'phone': phone,
                'email': f"{username}@company.com",
                'hire_date': date.today() - timedelta(days=365),
                'birth_date': date(1985, 1, 1),
                'salary': Decimal(str(salary))
            }
        )
        
        if created:
            print(f"✓ Создан сотрудник: {first_name} {last_name} - {position}")
        
        employees.append(employee)
    
    print("\nСоздаем договоры и заказы...")
    
    contracts_data = [
        {
            'number': 'DOG-2025-001',
            'client': clients[0],
            'employee': employees[0],
            'days_offset': -10,
            'orders': [
                {'service': 'Диагностика ноутбука', 'device': devices[0], 'quantity': 1, 'parts': ['Батарея для ноутбука 6-cell']},
                {'service': 'Замена батареи ноутбука', 'device': devices[0], 'quantity': 1, 'parts': []},
            ]
        },
        {
            'number': 'DOG-2025-002',
            'client': clients[1],
            'employee': employees[1],
            'days_offset': -7,
            'orders': [
                {'service': 'Диагностика компьютера', 'device': devices[1], 'quantity': 1, 'parts': []},
                {'service': 'Замена экрана ноутбука', 'device': devices[0], 'quantity': 1, 'parts': ['Экран 15.6" Full HD']},
            ]
        },
        {
            'number': 'DOG-2025-003',
            'client': clients[2],
            'employee': employees[2],
            'days_offset': -5,
            'orders': [
                {'service': 'Восстановление данных', 'device': devices[2], 'quantity': 1, 'parts': ['SSD 256GB']},
            ]
        },
        {
            'number': 'DOG-2025-004',
            'client': clients[3],
            'employee': employees[0],
            'days_offset': -3,
            'orders': [
                {'service': 'Ремонт материнской платы', 'device': devices[6], 'quantity': 1, 'parts': ['Материнская плата ASUS', 'RAM DDR4 8GB']},
                {'service': 'Установка ОС', 'device': devices[6], 'quantity': 1, 'parts': []},
            ]
        },
        {
            'number': 'DOG-2025-005',
            'client': clients[4],
            'employee': employees[1],
            'days_offset': -1,
            'orders': [
                {'service': 'Чистка от пыли', 'device': devices[7], 'quantity': 1, 'parts': []},
                {'service': 'Ремонт блока питания', 'device': devices[7], 'quantity': 1, 'parts': ['Блок питания 600W']},
            ]
        }
    ]
    
    for contract_data in contracts_data:
        date_signed = date.today() + timedelta(days=contract_data['days_offset'])
        deadline = date_signed + timedelta(days=7)
        
        contract, created = Contract.objects.get_or_create(
            number=contract_data['number'],
            defaults={
                'client': contract_data['client'],
                'employee': contract_data['employee'],
                'date_signed': date_signed,
                'deadline': deadline,
                'total_sum': Decimal('0.00'),
                'is_completed': contract_data['days_offset'] < -7  
            }
        )
        
        if created:
            print(f"✓ Создан договор: {contract_data['number']}")
            
            for order_data in contract_data['orders']:
                service = Service.objects.get(name=order_data['service'])
                device = order_data['device']
                
                order = Order.objects.create(
                    contract=contract,
                    service=service,
                    device=device,
                    quantity=order_data['quantity'],
                    status='completed' if contract.is_completed else 'in_progress'
                )
                
                # Добавляем запчасти к заказу
                for part_name in order_data['parts']:
                    try:
                        part = Part.objects.get(name=part_name)
                        order.parts.add(part)
                    except Part.DoesNotExist:
                        print(f"⚠ Запчасть не найдена: {part_name}")
                
                order.calculate_sums()
                order.save()
                
                print(f"  ✓ Создан заказ: {service.name} - {order.total_sum:.2f} руб.")
            
            contract.calculate_total_sum()
            print(f"  ✓ Итоговая сумма договора: {contract.total_sum:.2f} руб.")
    
    print(f"\n✅ Создание тестовых данных завершено!")
    print(f"📊 Создано:")
    print(f"  - Типов услуг: {ServiceType.objects.count()}")
    print(f"  - Услуг: {Service.objects.count()}")
    print(f"  - Типов устройств: {DeviceType.objects.count()}")
    print(f"  - Клиентов: {Client.objects.count()}")
    print(f"  - Устройств: {Device.objects.count()}")
    print(f"  - Запчастей: {Part.objects.count()}")
    print(f"  - Сотрудников: {Employee.objects.count()}")
    print(f"  - Договоров: {Contract.objects.count()}")
    print(f"  - Заказов: {Order.objects.count()}")

if __name__ == "__main__":
    create_test_data()
