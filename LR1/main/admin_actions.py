from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import *

def recalculate_all_costs(modeladmin, request, queryset):
    """Массовое пересчет всех стоимостей"""
    
    # Пересчитываем ремонты
    repairs_updated = 0
    for repair in Repair.objects.all():
        repair.calculate_total_cost()
        repair.save(update_fields=['total_cost'])
        repairs_updated += 1
    
    # Пересчитываем заказы
    orders_updated = 0
    for order in Order.objects.all():
        order.calculate_sums()
        order.save(update_fields=['service_sum', 'parts_sum', 'total_sum'])
        orders_updated += 1
    
    # Пересчитываем договоры
    contracts_updated = 0
    for contract in Contract.objects.all():
        contract.calculate_total_sum()
        contracts_updated += 1
    
    messages.success(
        request, 
        f'Пересчитано: {repairs_updated} ремонтов, {orders_updated} заказов, {contracts_updated} договоров'
    )

recalculate_all_costs.short_description = "Пересчитать все стоимости в системе"

def generate_monthly_report(modeladmin, request, queryset):
    """Генерация месячного отчета"""
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Статистика за текущий месяц
    monthly_repairs = Repair.objects.filter(
        created_at__year=current_year,
        created_at__month=current_month
    )
    
    monthly_contracts = Contract.objects.filter(
        date_signed__year=current_year,
        date_signed__month=current_month
    )
    
    context = {
        'month': current_month,
        'year': current_year,
        'repairs_count': monthly_repairs.count(),
        'repairs_total': monthly_repairs.aggregate(Sum('total_cost'))['total_cost__sum'] or 0,
        'contracts_count': monthly_contracts.count(),
        'contracts_total': monthly_contracts.aggregate(Sum('total_sum'))['total_sum__sum'] or 0,
        'completed_repairs': monthly_repairs.filter(status='completed').count(),
    }
    
    return render(request, 'admin/monthly_report.html', context)

generate_monthly_report.short_description = "Сгенерировать отчет за месяц"

def client_statistics_report(modeladmin, request, queryset):
    """Отчет по клиентам"""
    
    # Топ клиенты
    top_clients = Client.objects.annotate(
        repairs_count=Count('repairs'),
        total_spent=Sum('repairs__total_cost')
    ).filter(total_spent__isnull=False).order_by('-total_spent')[:20]
    
    # VIP клиенты
    vip_clients = Client.objects.filter(is_vip=True).annotate(
        repairs_count=Count('repairs'),
        total_spent=Sum('repairs__total_cost')
    )
    
    context = {
        'top_clients': top_clients,
        'vip_clients': vip_clients,
        'total_clients': Client.objects.count(),
        'active_clients': Client.objects.filter(repairs__isnull=False).distinct().count(),
    }
    
    return render(request, 'admin/client_statistics.html', context)

client_statistics_report.short_description = "Статистика по клиентам"

# Добавляем действия ко всем админ классам
admin.site.add_action(recalculate_all_costs)
admin.site.add_action(generate_monthly_report)
admin.site.add_action(client_statistics_report)
