"""
Административные отчеты для сервисного центра
"""
from django.contrib import admin
from django.db.models import Sum, Count, Avg, Q
from django.utils.html import format_html
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime, timedelta
from .models import Contract, Order, Client, Repair, SparePart, Service
import csv
import json


@staff_member_required
def reports_dashboard(request):
    """Главная панель отчетов"""
    
    # Статистика по договорам
    total_contracts = Contract.objects.count()
    completed_contracts = Contract.objects.filter(is_completed=True).count()
    contracts_this_month = Contract.objects.filter(
        date_signed__month=datetime.now().month,
        date_signed__year=datetime.now().year
    ).count()
    
    # Финансовая статистика
    total_revenue = Contract.objects.aggregate(total=Sum('total_sum'))['total'] or 0
    avg_contract_value = Contract.objects.aggregate(avg=Avg('total_sum'))['avg'] or 0
    revenue_this_month = Contract.objects.filter(
        date_signed__month=datetime.now().month,
        date_signed__year=datetime.now().year
    ).aggregate(total=Sum('total_sum'))['total'] or 0
    
    # Статистика по услугам
    most_popular_services = Service.objects.annotate(
        order_count=Count('order')
    ).order_by('-order_count')[:5]
    
    # Статистика по запчастям
    low_stock_parts = SparePart.objects.filter(quantity_in_stock__lt=5).count()
    most_used_parts = SparePart.objects.annotate(
        usage_count=Sum('repairsparepart__quantity')
    ).order_by('-usage_count')[:5]
    
    # Статистика по клиентам
    top_clients = Client.objects.annotate(
        total_spent=Sum('contract__total_sum')
    ).order_by('-total_spent')[:5]
    
    # VIP клиенты
    vip_clients_count = Client.objects.filter(is_vip=True).count()
    
    context = {
        'title': 'Отчеты и аналитика сервисного центра',
        'total_contracts': total_contracts,
        'completed_contracts': completed_contracts,
        'contracts_this_month': contracts_this_month,
        'completion_rate': round((completed_contracts / total_contracts * 100) if total_contracts > 0 else 0, 1),
        'total_revenue': total_revenue,
        'avg_contract_value': avg_contract_value,
        'revenue_this_month': revenue_this_month,
        'most_popular_services': most_popular_services,
        'low_stock_parts': low_stock_parts,
        'most_used_parts': most_used_parts,
        'top_clients': top_clients,
        'vip_clients_count': vip_clients_count,
    }
    
    return render(request, 'admin/reports_dashboard.html', context)


@staff_member_required
def financial_report(request):
    """Финансовый отчет"""
    
    # Получаем параметры фильтрации
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    contracts = Contract.objects.all()
    
    if start_date:
        contracts = contracts.filter(date_signed__gte=start_date)
    if end_date:
        contracts = contracts.filter(date_signed__lte=end_date)
    
    # Финансовая статистика
    total_revenue = contracts.aggregate(total=Sum('total_sum'))['total'] or 0
    total_services_cost = contracts.aggregate(
        total=Sum('order__service_sum')
    )['total'] or 0
    total_parts_cost = contracts.aggregate(
        total=Sum('order__parts_sum')
    )['total'] or 0
    
    # Статистика по месяцам
    monthly_stats = []
    for i in range(12):
        month_start = datetime.now().replace(day=1, month=datetime.now().month-i if datetime.now().month-i > 0 else 12+datetime.now().month-i)
        if datetime.now().month-i <= 0:
            month_start = month_start.replace(year=datetime.now().year-1)
        
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        month_contracts = contracts.filter(
            date_signed__gte=month_start,
            date_signed__lte=month_end
        )
        
        month_revenue = month_contracts.aggregate(total=Sum('total_sum'))['total'] or 0
        month_count = month_contracts.count()
        
        monthly_stats.append({
            'month': month_start.strftime('%B %Y'),
            'revenue': month_revenue,
            'contracts_count': month_count,
            'avg_contract': month_revenue / month_count if month_count > 0 else 0
        })
    
    context = {
        'title': 'Финансовый отчет',
        'total_revenue': total_revenue,
        'total_services_cost': total_services_cost,
        'total_parts_cost': total_parts_cost,
        'contracts_count': contracts.count(),
        'avg_contract_value': total_revenue / contracts.count() if contracts.count() > 0 else 0,
        'monthly_stats': monthly_stats[:6],  # Последние 6 месяцев
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'admin/financial_report.html', context)


@staff_member_required
def client_analytics(request):
    """Аналитика по клиентам"""
    
    # Топ клиенты по сумме
    top_clients_by_sum = Client.objects.annotate(
        total_spent=Sum('contract__total_sum'),
        contracts_count=Count('contract')
    ).order_by('-total_spent')[:10]
    
    # Топ клиенты по количеству договоров
    top_clients_by_contracts = Client.objects.annotate(
        contracts_count=Count('contract'),
        total_spent=Sum('contract__total_sum')
    ).order_by('-contracts_count')[:10]
    
    # VIP клиенты
    vip_clients = Client.objects.filter(is_vip=True).annotate(
        total_spent=Sum('contract__total_sum'),
        contracts_count=Count('contract')
    )
    
    # Новые клиенты за последний месяц
    month_ago = datetime.now() - timedelta(days=30)
    new_clients = Client.objects.filter(registration_date__gte=month_ago)
    
    context = {
        'title': 'Аналитика по клиентам',
        'top_clients_by_sum': top_clients_by_sum,
        'top_clients_by_contracts': top_clients_by_contracts,
        'vip_clients': vip_clients,
        'new_clients': new_clients,
        'total_clients': Client.objects.count(),
        'vip_percentage': round((vip_clients.count() / Client.objects.count() * 100) if Client.objects.count() > 0 else 0, 1),
    }
    
    return render(request, 'admin/client_analytics.html', context)


@staff_member_required
def parts_analytics(request):
    """Аналитика по запчастям"""
    
    # Самые используемые запчасти
    most_used_parts = SparePart.objects.annotate(
        usage_count=Sum('repairsparepart__quantity')
    ).order_by('-usage_count')[:10]
    
    # Запчасти с низким остатком
    low_stock_parts = SparePart.objects.filter(quantity_in_stock__lt=5)
    
    # Запчасти которых нет в наличии
    out_of_stock_parts = SparePart.objects.filter(quantity_in_stock=0)
    
    # Самые дорогие запчасти
    expensive_parts = SparePart.objects.order_by('-price')[:10]
    
    # Статистика по категориям
    categories_stats = []
    categories = SparePart.objects.values_list('category', flat=True).distinct()
    
    for category in categories:
        category_parts = SparePart.objects.filter(category=category)
        total_value = sum(part.price * part.quantity_in_stock for part in category_parts)
        
        categories_stats.append({
            'category': category,
            'parts_count': category_parts.count(),
            'total_stock': category_parts.aggregate(total=Sum('quantity_in_stock'))['total'] or 0,
            'total_value': total_value,
            'avg_price': category_parts.aggregate(avg=Avg('price'))['avg'] or 0
        })
    
    context = {
        'title': 'Аналитика по запчастям',
        'most_used_parts': most_used_parts,
        'low_stock_parts': low_stock_parts,
        'out_of_stock_parts': out_of_stock_parts,
        'expensive_parts': expensive_parts,
        'categories_stats': categories_stats,
        'total_parts': SparePart.objects.count(),
        'total_stock_value': sum(part.price * part.quantity_in_stock for part in SparePart.objects.all()),
    }
    
    return render(request, 'admin/parts_analytics.html', context)


@staff_member_required
def export_contracts_csv(request):
    """Экспорт всех договоров в CSV"""
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="all_contracts.csv"'
    response.write('\ufeff')  # BOM для Excel
    
    writer = csv.writer(response)
    writer.writerow([
        'Номер договора', 'Клиент', 'Телефон клиента', 'Сотрудник', 
        'Дата заключения', 'Срок выполнения', 'Количество услуг',
        'Стоимость услуг', 'Стоимость запчастей', 'Итоговая сумма',
        'Выполнение %', 'Статус', 'Дата создания'
    ])
    
    contracts = Contract.objects.select_related('client', 'employee').all()
    
    for contract in contracts:
        writer.writerow([
            contract.number,
            contract.client.user.get_full_name(),
            contract.client.phone,
            contract.employee.user.get_full_name() if contract.employee else 'Не назначен',
            contract.date_signed.strftime('%d.%m.%Y'),
            contract.deadline.strftime('%d.%m.%Y'),
            contract.get_services_count(),
            f"{contract.get_total_services_cost():.2f}",
            f"{contract.get_total_parts_cost():.2f}",
            f"{contract.total_sum:.2f}",
            f"{contract.get_completion_status():.1f}%",
            'Выполнен' if contract.is_completed else 'В работе',
            contract.created_at.strftime('%d.%m.%Y %H:%M')
        ])
    
    return response


@staff_member_required
def api_contract_stats(request):
    """API для получения статистики договоров (для графиков)"""
    
    # Статистика по месяцам за последний год
    monthly_data = []
    for i in range(12):
        date = datetime.now() - timedelta(days=30*i)
        month_start = date.replace(day=1)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        contracts_count = Contract.objects.filter(
            date_signed__gte=month_start,
            date_signed__lte=month_end
        ).count()
        
        revenue = Contract.objects.filter(
            date_signed__gte=month_start,
            date_signed__lte=month_end
        ).aggregate(total=Sum('total_sum'))['total'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%Y-%m'),
            'contracts': contracts_count,
            'revenue': float(revenue)
        })
    
    return JsonResponse({
        'monthly_data': list(reversed(monthly_data))
    })
