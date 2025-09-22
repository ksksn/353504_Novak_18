#!/usr/bin/env python
"""
Тест для проверки работы админ-панели
"""
import os
import sys
import django

# Настройка Django
sys.path.append('/Users/ksenianovak/Desktop/qqq')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_website.settings')
django.setup()

from main.admin_new import admin_site
from main.models import Client, Contract, Order

def test_admin_registration():
    """Проверка регистрации моделей в админке"""
    print("=== Тест регистрации моделей в админке ===\n")
    
    # Проверим, какие модели зарегистрированы
    registered_models = admin_site._registry
    
    print(f"Всего зарегистрированных моделей: {len(registered_models)}")
    print("\nЗарегистрированные модели:")
    
    for model, admin_class in registered_models.items():
        print(f"  • {model.__name__} -> {admin_class.__class__.__name__}")
    
    # Проверим URL-маршруты
    print(f"\n=== URL-маршруты админки ===")
    try:
        from django.urls import reverse
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/admin/')
        
        # Проверим основную страницу админки
        admin_index_url = reverse('admin:index', current_app=admin_site.name)
        print(f"Основная страница: {admin_index_url}")
        
        # Проверим URL для добавления клиента
        try:
            client_add_url = reverse('admin:main_client_add', current_app=admin_site.name)
            print(f"Добавление клиента: {client_add_url}")
        except Exception as e:
            print(f"❌ Ошибка URL для добавления клиента: {e}")
        
        # Проверим URL для списка договоров
        try:
            contract_list_url = reverse('admin:main_contract_changelist', current_app=admin_site.name)
            print(f"Список договоров: {contract_list_url}")
        except Exception as e:
            print(f"❌ Ошибка URL для списка договоров: {e}")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке URL: {e}")

def test_model_access():
    """Проверка доступа к моделям"""
    print(f"\n=== Тест доступа к моделям ===")
    
    try:
        # Проверим количество записей
        clients_count = Client.objects.count()
        contracts_count = Contract.objects.count()
        orders_count = Order.objects.count()
        
        print(f"Клиентов в БД: {clients_count}")
        print(f"Договоров в БД: {contracts_count}")
        print(f"Заказов в БД: {orders_count}")
        
        if clients_count > 0:
            first_client = Client.objects.first()
            print(f"Первый клиент: {first_client}")
            
    except Exception as e:
        print(f"❌ Ошибка при доступе к моделям: {e}")

if __name__ == "__main__":
    test_admin_registration()
    test_model_access()
    print("\n✅ Тестирование завершено!")
