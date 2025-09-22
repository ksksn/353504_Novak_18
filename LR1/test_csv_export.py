#!/usr/bin/env python
"""
Тестирование экспорта данных в CSV
"""
import os
import sys
import django

# Настройка Django
sys.path.append('/Users/ksenianovak/Desktop/qqq')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_website.settings')
django.setup()

import requests
from django.contrib.auth import get_user_model

def test_csv_export():
    """Тестирование экспорта договоров в CSV"""
    print("=== Тест экспорта договоров в CSV ===\n")
    
    # URL для экспорта
    export_url = 'http://127.0.0.1:8000/admin/reports/export-contracts/'
    
    try:
        # Проверяем, что сервер запущен
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        print("✓ Сервер доступен")
        
        # Пытаемся получить CSV без авторизации
        csv_response = requests.get(export_url, timeout=5)
        print(f"Статус запроса без авторизации: {csv_response.status_code}")
        
        if csv_response.status_code == 302:
            print("✓ Правильная переадресация на страницу входа")
        elif csv_response.status_code == 200:
            print("⚠ Доступ к экспорту без авторизации (возможная проблема безопасности)")
        
    except requests.ConnectionError:
        print("❌ Сервер недоступен. Убедитесь, что Django сервер запущен.")
        return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False
    
    return True

def show_contract_summary():
    """Показать сводку по договорам"""
    from main.models import Contract, Order
    
    print("\n=== Сводка по договорам в базе данных ===")
    
    contracts = Contract.objects.all().order_by('-total_sum')
    total_contracts = contracts.count()
    total_sum = sum(c.total_sum or 0 for c in contracts)
    
    print(f"Всего договоров: {total_contracts}")
    print(f"Общая сумма: {total_sum:.2f} руб.")
    
    if contracts:
        print("\nТоп-5 договоров:")
        for i, contract in enumerate(contracts[:5], 1):
            client_name = contract.client.full_name if contract.client else "Неизвестно"
            print(f"  {i}. {contract.number} - {contract.total_sum:.2f} руб. ({client_name})")
    
    orders = Order.objects.all()
    print(f"\nВсего заказов: {orders.count()}")
    
    return True

if __name__ == "__main__":
    # Показать сводку
    show_contract_summary()
    
    # Тестировать экспорт
    test_csv_export()
    
    print("\n✅ Тестирование завершено!")
