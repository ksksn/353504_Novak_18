"""
Утилиты для админ-панели сервисного центра
"""
from django.utils.html import format_html
from django.contrib.admin import helpers
from django.contrib import messages
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Contract, Order, Repair, Client


def calculate_repair_total(repair):
    """Рассчитать общую стоимость ремонта"""
    labor_cost = repair.labor_cost or Decimal('0.00')
    parts_cost = repair.repair_spare_parts.aggregate(
        total=Sum('total_price')
    )['total'] or Decimal('0.00')
    return labor_cost + parts_cost


def format_money(amount):
    """Форматировать сумму денег"""
    if amount is None:
        return "0.00 руб."
    return f"{amount:.2f} руб."


def get_status_badge(status):
    """Получить HTML badge для статуса"""
    status_colors = {
        'pending': 'warning',
        'in_progress': 'info',
        'completed': 'success',
        'cancelled': 'danger',
        'paid': 'success',
        'unpaid': 'warning',
    }
    
    status_names = {
        'pending': 'Ожидание',
        'in_progress': 'В работе',
        'completed': 'Завершен',
        'cancelled': 'Отменен',
        'paid': 'Оплачен',
        'unpaid': 'Не оплачен',
    }
    
    color = status_colors.get(status, 'secondary')
    name = status_names.get(status, status)
    
    return format_html(
        '<span class="badge badge-{}">{}</span>',
        color, name
    )


def get_priority_badge(priority):
    """Получить HTML badge для приоритета"""
    priority_colors = {
        'low': 'secondary',
        'normal': 'primary',
        'high': 'warning',
        'urgent': 'danger',
    }
    
    priority_names = {
        'low': 'Низкий',
        'normal': 'Обычный',
        'high': 'Высокий',
        'urgent': 'Срочный',
    }
    
    color = priority_colors.get(priority, 'secondary')
    name = priority_names.get(priority, priority)
    
    return format_html(
        '<span class="badge badge-{}">{}</span>',
        color, name
    )


def generate_contract_number():
    """Генерировать номер договора"""
    from datetime import datetime
    today = datetime.now()
    year_suffix = str(today.year)[-2:]
    month = f"{today.month:02d}"
    
    # Найти последний номер в этом месяце
    prefix = f"{year_suffix}{month}"
    last_contract = Contract.objects.filter(
        number__startswith=prefix
    ).order_by('number').last()
    
    if last_contract:
        last_num = int(last_contract.number[-4:])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"{prefix}{new_num:04d}"


def get_weekly_stats():
    """Получить статистику за неделю"""
    week_ago = datetime.now() - timedelta(days=7)
    
    stats = {
        'new_contracts': Contract.objects.filter(
            created_at__gte=week_ago
        ).count(),
        'completed_repairs': Repair.objects.filter(
            completed_at__gte=week_ago,
            status='completed'
        ).count(),
        'total_revenue': Contract.objects.filter(
            created_at__gte=week_ago,
            is_completed=True
        ).aggregate(total=Sum('total_sum'))['total'] or Decimal('0.00'),
        'new_clients': Client.objects.filter(
            registration_date__gte=week_ago
        ).count(),
    }
    
    return stats


def get_monthly_stats():
    """Получить статистику за месяц"""
    month_ago = datetime.now() - timedelta(days=30)
    
    stats = {
        'contracts_count': Contract.objects.filter(
            created_at__gte=month_ago
        ).count(),
        'repairs_count': Repair.objects.filter(
            created_at__gte=month_ago
        ).count(),
        'revenue': Contract.objects.filter(
            created_at__gte=month_ago,
            is_completed=True
        ).aggregate(total=Sum('total_sum'))['total'] or Decimal('0.00'),
        'avg_repair_cost': Repair.objects.filter(
            created_at__gte=month_ago,
            status='completed'
        ).aggregate(avg=Sum('total_cost'))['avg'] or Decimal('0.00'),
    }
    
    return stats


def export_contracts_csv(queryset):
    """Экспорт договоров в CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contracts.csv"'
    response.write('\ufeff')  # BOM для правильного отображения в Excel
    
    writer = csv.writer(response)
    writer.writerow([
        'Номер договора',
        'Клиент', 
        'Дата создания',
        'Общая сумма',
        'Статус',
        'Завершен'
    ])
    
    for contract in queryset:
        writer.writerow([
            contract.number,
            contract.client.user.get_full_name(),
            contract.created_at.strftime('%d.%m.%Y'),
            contract.total_sum,
            contract.get_status_display() if hasattr(contract, 'get_status_display') else '',
            'Да' if contract.is_completed else 'Нет'
        ])
    
    return response


def export_repairs_csv(queryset):
    """Экспорт ремонтов в CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="repairs.csv"'
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow([
        'ID',
        'Клиент',
        'Устройство',
        'Описание',
        'Статус',
        'Стоимость работ',
        'Общая стоимость',
        'Дата создания',
        'Дата завершения'
    ])
    
    for repair in queryset:
        writer.writerow([
            repair.id,
            repair.client.user.get_full_name(),
            f"{repair.device.name} {repair.device.model}",
            repair.description,
            repair.get_status_display(),
            repair.labor_cost,
            repair.total_cost,
            repair.created_at.strftime('%d.%m.%Y %H:%M'),
            repair.completed_at.strftime('%d.%m.%Y %H:%M') if repair.completed_at else ''
        ])
    
    return response


def bulk_update_status(queryset, new_status, user):
    """Массовое обновление статуса"""
    updated_count = 0
    
    for obj in queryset:
        obj.status = new_status
        if new_status == 'completed' and hasattr(obj, 'completed_at'):
            obj.completed_at = datetime.now()
        obj.save()
        updated_count += 1
    
    return updated_count


class AdminStatsWidget:
    """Виджет для отображения статистики в админке"""
    
    @staticmethod
    def get_dashboard_stats():
        """Получить статистику для дашборда"""
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        return {
            'today': {
                'contracts': Contract.objects.filter(created_at__date=today).count(),
                'repairs': Repair.objects.filter(created_at__date=today).count(),
                'revenue': Contract.objects.filter(
                    created_at__date=today,
                    is_completed=True
                ).aggregate(total=Sum('total_sum'))['total'] or Decimal('0.00'),
            },
            'week': {
                'contracts': Contract.objects.filter(created_at__date__gte=week_ago).count(),
                'repairs': Repair.objects.filter(created_at__date__gte=week_ago).count(),
                'revenue': Contract.objects.filter(
                    created_at__date__gte=week_ago,
                    is_completed=True
                ).aggregate(total=Sum('total_sum'))['total'] or Decimal('0.00'),
            },
            'month': {
                'contracts': Contract.objects.filter(created_at__date__gte=month_ago).count(),
                'repairs': Repair.objects.filter(created_at__date__gte=month_ago).count(),
                'revenue': Contract.objects.filter(
                    created_at__date__gte=month_ago,
                    is_completed=True
                ).aggregate(total=Sum('total_sum'))['total'] or Decimal('0.00'),
            },
            'total': {
                'contracts': Contract.objects.count(),
                'repairs': Repair.objects.count(),
                'clients': Client.objects.count(),
                'revenue': Contract.objects.filter(
                    is_completed=True
                ).aggregate(total=Sum('total_sum'))['total'] or Decimal('0.00'),
            }
        }


def create_admin_notification(user, message, type='info'):
    """Создать уведомление для админа"""
    # Здесь можно добавить логику сохранения уведомлений в БД
    # Пока используем стандартные Django messages
    message_types = {
        'info': messages.INFO,
        'success': messages.SUCCESS,
        'warning': messages.WARNING,
        'error': messages.ERROR,
    }
    
    level = message_types.get(type, messages.INFO)
    return message, level


def validate_contract_data(contract):
    """Валидация данных договора"""
    errors = []
    
    if not contract.client:
        errors.append("Не указан клиент")
    
    if not contract.orders.exists():
        errors.append("Договор не содержит заказов")
    
    if contract.total_sum <= 0:
        errors.append("Общая сумма должна быть больше нуля")
    
    return errors


def auto_calculate_contract_sum(contract):
    """Автоматический расчет суммы договора"""
    total = contract.orders.aggregate(
        total=Sum('total_sum')
    )['total'] or Decimal('0.00')
    
    contract.total_sum = total
    contract.save(update_fields=['total_sum'])
    
    return total
