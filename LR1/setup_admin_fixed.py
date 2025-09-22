#!/usr/bin/env python
"""
Скрипт для создания суперпользователя и наполнения базы данных тестовыми данными
"""
import os
import sys
import django
from datetime import date, datetime, timedelta

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_website.settings')
django.setup()

# Импорт моделей после настройки Django
from django.contrib.auth.models import User
from main.models import (
    Client, Device, DeviceType, SparePart, 
    Service, ServiceType, Employee, EmployeeSpecialization,
    Repair, Contract, Order
)

def create_superuser():
    """Создание суперпользователя admin/admin"""
    print("=== Создание суперпользователя ===")
    
    if User.objects.filter(username='admin').exists():
        print("✓ Суперпользователь уже существует")
        return
    
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin',
        first_name='Администратор',
        last_name='Системы'
    )
    print("✓ Создан суперпользователь: admin / admin")

def create_test_data():
    """Создание тестовых данных"""
    print("\n=== Создание тестовых данных ===")
    
    # 1. Типы устройств
    device_types = ['Смартфон', 'Планшет', 'Ноутбук', 'Компьютер', 'Телевизор']
    for type_name in device_types:
        device_type, created = DeviceType.objects.get_or_create(
            name=type_name,
            defaults={'description': f'Ремонт {type_name.lower()}ов'}
        )
        if created:
            print(f"✓ Создан тип устройства: {type_name}")
    
    # 2. Запчасти
    spare_parts_data = [
        {'name': 'Экран iPhone 12', 'category': 'Экран', 'price': 150.00, 'quantity_in_stock': 10},
        {'name': 'Батарея Samsung Galaxy', 'category': 'Батарея', 'price': 50.00, 'quantity_in_stock': 15},
        {'name': 'Экран Xiaomi Redmi', 'category': 'Экран', 'price': 80.00, 'quantity_in_stock': 8},
    ]
    
    for part_data in spare_parts_data:
        spare_part, created = SparePart.objects.get_or_create(
            name=part_data['name'],
            defaults=part_data
        )
        if created:
            print(f"✓ Создана запчасть: {part_data['name']}")
    
    # 3. Специализации сотрудников
    specializations_data = [
        {'name': 'Ремонт смартфонов', 'description': 'Диагностика и ремонт мобильных устройств'},
        {'name': 'Ремонт ноутбуков', 'description': 'Диагностика и ремонт портативных компьютеров'},
        {'name': 'Диагностика', 'description': 'Первичная диагностика неисправностей'},
    ]
    
    for spec_data in specializations_data:
        spec, created = EmployeeSpecialization.objects.get_or_create(
            name=spec_data['name'],
            defaults=spec_data
        )
        if created:
            print(f"✓ Создана специализация: {spec_data['name']}")
    
    # 4. Сотрудники
    phone_spec = EmployeeSpecialization.objects.get(name='Ремонт смартфонов')
    diag_spec = EmployeeSpecialization.objects.get(name='Диагностика')
    
    # Создание пользователей для сотрудников
    emp1_user, created = User.objects.get_or_create(
        username='ivan_petrov',
        defaults={
            'email': 'ivan@service.com',
            'first_name': 'Иван',
            'last_name': 'Петров'
        }
    )
    if created:
        emp1_user.set_password('emp123')
        emp1_user.save()
    
    emp2_user, created = User.objects.get_or_create(
        username='maria_sidorova',
        defaults={
            'email': 'maria@service.com',
            'first_name': 'Мария',
            'last_name': 'Сидорова'
        }
    )
    if created:
        emp2_user.set_password('emp123')
        emp2_user.save()
    
    employees_data = [
        {
            'user': emp1_user,
            'position': 'technician',
            'description': 'Специалист по ремонту мобильных устройств',
            'phone': '+375 (29) 111-11-11',
            'email': 'ivan@service.com',
            'birth_date': date(1985, 5, 15),
            'hire_date': date(2020, 1, 10),
            'salary': 1200.00
        },
        {
            'user': emp2_user,
            'position': 'technician',
            'description': 'Специалист по диагностике устройств',
            'phone': '+375 (29) 222-22-22',
            'email': 'maria@service.com',
            'birth_date': date(1990, 8, 20),
            'hire_date': date(2021, 3, 15),
            'salary': 1000.00
        }
    ]
    
    for emp_data in employees_data:
        employee, created = Employee.objects.get_or_create(
            user=emp_data['user'],
            defaults=emp_data
        )
        if created:
            print(f"✓ Создан сотрудник: {emp_data['user'].get_full_name()}")
            # Добавляем специализации
            if emp_data['user'] == emp1_user:
                employee.specializations.add(phone_spec)
            elif emp_data['user'] == emp2_user:
                employee.specializations.add(diag_spec)
    
    # 5. Типы услуг
    service_types_data = [
        {'name': 'Диагностика', 'description': 'Выявление неисправностей устройства'},
        {'name': 'Замена экрана', 'description': 'Замена поврежденного дисплея'},
        {'name': 'Замена батареи', 'description': 'Замена аккумулятора'},
    ]
    
    for st_data in service_types_data:
        service_type, created = ServiceType.objects.get_or_create(
            name=st_data['name'],
            defaults=st_data
        )
        if created:
            print(f"✓ Создан тип услуги: {st_data['name']}")
    
    # 6. Услуги
    diag_type = ServiceType.objects.get(name='Диагностика')
    screen_type = ServiceType.objects.get(name='Замена экрана')
    
    services_data = [
        {'name': 'Диагностика смартфона', 'service_type': diag_type, 'price': 15.00, 'description': 'Полная диагностика устройства'},
        {'name': 'Замена экрана iPhone', 'service_type': screen_type, 'price': 100.00, 'description': 'Замена поврежденного экрана iPhone'},
        {'name': 'Замена экрана Android', 'service_type': screen_type, 'price': 80.00, 'description': 'Замена экрана Android устройств'},
    ]
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults=service_data
        )
        if created:
            print(f"✓ Создана услуга: {service_data['name']}")
    
    # 7. Создание тестового клиента
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
        print(f"✓ Создан пользователь: testclient")
    
    test_client, created = Client.objects.get_or_create(
        user=test_user,
        defaults={
            'phone': '+375 (29) 123-45-67',
            'address': 'г. Минск, ул. Тестовая, д. 1',
            'birth_date': date(1990, 1, 1)
        }
    )
    if created:
        print(f"✓ Создан клиент: {test_client}")
    
    # 8. Устройства клиента
    smartphone_type = DeviceType.objects.get(name='Смартфон')
    devices_data = [
        {
            'client': test_client,
            'device_type': smartphone_type,
            'name': 'iPhone 12 Pro',
            'model': 'A2341',
            'serial_number': 'IP12001'
        },
        {
            'client': test_client,
            'device_type': smartphone_type,
            'name': 'Samsung Galaxy S21',
            'model': 'SM-G991B',
            'serial_number': 'SGS21001'
        }
    ]
    
    for device_data in devices_data:
        device, created = Device.objects.get_or_create(
            serial_number=device_data['serial_number'],
            defaults=device_data
        )
        if created:
            print(f"✓ Создано устройство: {device_data['name']} {device_data['model']}")
    
    # 9. Ремонты
    iphone_device = Device.objects.get(serial_number='IP12001')
    
    repair, created = Repair.objects.get_or_create(
        device=iphone_device,
        defaults={
            'client': test_client,
            'description': 'Разбился экран после падения',
            'status': 'in_progress',
            'labor_cost': 50.00,
            'total_cost': 200.00
        }
    )
    if created:
        print(f"✓ Создан ремонт для {iphone_device.name}")
    
    # 10. Договор
    contract, created = Contract.objects.get_or_create(
        client=test_client,
        defaults={
            'number': 'DOG-2024-001',
            'date_signed': date.today(),
            'deadline': date.today() + timedelta(days=7),
            'total_sum': 200.00,
            'is_completed': False
        }
    )
    if created:
        print(f"✓ Создан договор: {contract.number}")
    
    print("\n✅ Все тестовые данные созданы успешно!")

def main():
    print("=== Настройка админки ремонтного сервиса ===\n")
    
    try:
        create_superuser()
        create_test_data()
        
        print("\n🎉 Настройка завершена!")
        print("📋 Данные для входа в админку:")
        print("   URL: http://127.0.0.1:8000/admin/")
        print("   Логин: admin")
        print("   Пароль: admin")
        print("\n🧪 Тестовый клиент:")
        print("   Логин: testclient")
        print("   Пароль: testpass")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise

if __name__ == '__main__':
    main()
