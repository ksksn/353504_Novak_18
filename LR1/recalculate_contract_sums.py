#!/usr/bin/env python
"""
Скрипт для пересчета итоговых сумм всех договоров в системе
Запуск: python recalculate_contract_sums.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_website.settings')
django.setup()

from main.models import Contract, Order
from django.db.models import Sum

def recalculate_all_contract_sums():
    """Пересчитать суммы всех договоров"""
    
    print("=== Пересчет итоговых сумм договоров ===\n")
    
    contracts = Contract.objects.all()
    total_contracts = contracts.count()
    updated_count = 0
    errors_count = 0
    
    print(f"Найдено договоров: {total_contracts}")
    print("Начинаем пересчет...\n")
    
    for i, contract in enumerate(contracts, 1):
        try:
            old_sum = contract.total_sum
            
            # Пересчитываем сумму договора
            new_sum = contract.calculate_total_sum()
            
            if old_sum != new_sum:
                print(f"[{i}/{total_contracts}] Договор {contract.number}:")
                print(f"  Было: {old_sum:.2f} руб.")
                print(f"  Стало: {new_sum:.2f} руб.")
                print(f"  Разница: {new_sum - old_sum:.2f} руб.")
                updated_count += 1
            else:
                print(f"[{i}/{total_contracts}] Договор {contract.number}: сумма не изменилась ({old_sum:.2f} руб.)")
                
        except Exception as e:
            print(f"[{i}/{total_contracts}] ОШИБКА в договоре {contract.number}: {e}")
            errors_count += 1
    
    print(f"\n=== Результаты пересчета ===")
    print(f"Всего договоров: {total_contracts}")
    print(f"Обновлено: {updated_count}")
    print(f"Без изменений: {total_contracts - updated_count - errors_count}")
    print(f"Ошибок: {errors_count}")
    print("="*40)

def recalculate_all_order_sums():
    """Пересчитать суммы всех заказов"""
    
    print("\n=== Пересчет сумм заказов ===\n")
    
    orders = Order.objects.all()
    total_orders = orders.count()
    updated_count = 0
    errors_count = 0
    
    print(f"Найдено заказов: {total_orders}")
    print("Начинаем пересчет...\n")
    
    for i, order in enumerate(orders, 1):
        try:
            old_total = order.total_sum
            old_service = order.service_sum
            old_parts = order.parts_sum
            
            # Пересчитываем суммы заказа
            new_total = order.calculate_sums()
            order.save()
            
            if (old_total != order.total_sum or 
                old_service != order.service_sum or 
                old_parts != order.parts_sum):
                
                print(f"[{i}/{total_orders}] Заказ {order.id} (Договор {order.contract.number}):")
                print(f"  Услуги: {old_service:.2f} → {order.service_sum:.2f} руб.")
                print(f"  Запчасти: {old_parts:.2f} → {order.parts_sum:.2f} руб.")
                print(f"  Итого: {old_total:.2f} → {order.total_sum:.2f} руб.")
                updated_count += 1
            else:
                print(f"[{i}/{total_orders}] Заказ {order.id}: суммы не изменились")
                
        except Exception as e:
            print(f"[{i}/{total_orders}] ОШИБКА в заказе {order.id}: {e}")
            errors_count += 1
    
    print(f"\n=== Результаты пересчета заказов ===")
    print(f"Всего заказов: {total_orders}")
    print(f"Обновлено: {updated_count}")
    print(f"Без изменений: {total_orders - updated_count - errors_count}")
    print(f"Ошибок: {errors_count}")
    print("="*40)

def show_contracts_summary():
    """Показать сводку по договорам"""
    
    print("\n=== Сводка по договорам ===\n")
    
    # Общая статистика
    total_contracts = Contract.objects.count()
    completed_contracts = Contract.objects.filter(is_completed=True).count()
    
    # Финансовая статистика
    total_sum = Contract.objects.aggregate(total=Sum('total_sum'))['total'] or 0
    completed_sum = Contract.objects.filter(is_completed=True).aggregate(total=Sum('total_sum'))['total'] or 0
    
    # Статистика по заказам
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(status='completed').count()
    
    print(f"Договоры:")
    print(f"  Всего: {total_contracts}")
    print(f"  Выполнено: {completed_contracts} ({completed_contracts/total_contracts*100:.1f}%)")
    print(f"  В работе: {total_contracts - completed_contracts}")
    
    print(f"\nФинансы:")
    print(f"  Общая сумма всех договоров: {total_sum:.2f} руб.")
    print(f"  Сумма выполненных договоров: {completed_sum:.2f} руб.")
    print(f"  Средняя сумма договора: {total_sum/total_contracts:.2f} руб.")
    
    print(f"\nЗаказы:")
    print(f"  Всего заказов: {total_orders}")
    print(f"  Выполнено: {completed_orders} ({completed_orders/total_orders*100:.1f}%)")
    print(f"  В работе: {total_orders - completed_orders}")
    
    # Топ-5 договоров по сумме
    print(f"\nТоп-5 договоров по сумме:")
    top_contracts = Contract.objects.order_by('-total_sum')[:5]
    for i, contract in enumerate(top_contracts, 1):
        print(f"  {i}. {contract.number} - {contract.total_sum:.2f} руб. ({contract.client.user.get_full_name()})")
    
    print("="*40)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Пересчет сумм договоров и заказов')
    parser.add_argument('--contracts-only', action='store_true', 
                       help='Пересчитать только суммы договоров')
    parser.add_argument('--orders-only', action='store_true',
                       help='Пересчитать только суммы заказов')
    parser.add_argument('--summary-only', action='store_true',
                       help='Показать только сводку без пересчета')
    
    args = parser.parse_args()
    
    if args.summary_only:
        show_contracts_summary()
    elif args.contracts_only:
        recalculate_all_contract_sums()
        show_contracts_summary()
    elif args.orders_only:
        recalculate_all_order_sums()
    else:
        # По умолчанию пересчитываем все
        recalculate_all_order_sums()
        recalculate_all_contract_sums()
        show_contracts_summary()
