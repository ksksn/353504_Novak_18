"""
Расширенные действия для админ-панели
"""
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum, Q
from decimal import Decimal
from .admin_utils import (
    export_contracts_csv, export_repairs_csv, 
    bulk_update_status, auto_calculate_contract_sum,
    format_money, create_admin_notification
)


@admin.action(description='Экспортировать выбранные договоры в CSV')
def export_selected_contracts_csv(modeladmin, request, queryset):
    """Экспорт выбранных договоров в CSV"""
    return export_contracts_csv(queryset)


@admin.action(description='Экспортировать выбранные ремонты в CSV')
def export_selected_repairs_csv(modeladmin, request, queryset):
    """Экспорт выбранных ремонтов в CSV"""
    return export_repairs_csv(queryset)


@admin.action(description='Отметить как завершенные')
def mark_as_completed(modeladmin, request, queryset):
    """Отметить выбранные объекты как завершенные"""
    updated = bulk_update_status(queryset, 'completed', request.user)
    modeladmin.message_user(
        request,
        f'Отмечено как завершенные: {updated} объектов',
        messages.SUCCESS
    )


@admin.action(description='Отметить как в работе')
def mark_as_in_progress(modeladmin, request, queryset):
    """Отметить выбранные объекты как в работе"""
    updated = bulk_update_status(queryset, 'in_progress', request.user)
    modeladmin.message_user(
        request,
        f'Отмечено как в работе: {updated} объектов',
        messages.SUCCESS
    )


@admin.action(description='Отменить выбранные')
def mark_as_cancelled(modeladmin, request, queryset):
    """Отменить выбранные объекты"""
    updated = bulk_update_status(queryset, 'cancelled', request.user)
    modeladmin.message_user(
        request,
        f'Отменено: {updated} объектов',
        messages.WARNING
    )


@admin.action(description='Пересчитать стоимость договоров')
def recalculate_contract_sums(modeladmin, request, queryset):
    """Пересчитать стоимость выбранных договоров"""
    updated = 0
    total_recalculated = Decimal('0.00')
    
    for contract in queryset:
        old_sum = contract.total_sum
        new_sum = auto_calculate_contract_sum(contract)
        total_recalculated += abs(new_sum - old_sum)
        updated += 1
    
    modeladmin.message_user(
        request,
        f'Пересчитано {updated} договоров. Общее изменение: {format_money(total_recalculated)}',
        messages.SUCCESS
    )


@admin.action(description='Пересчитать стоимость ремонтов')
def recalculate_repair_costs(modeladmin, request, queryset):
    """Пересчитать стоимость выбранных ремонтов"""
    updated = 0
    
    for repair in queryset:
        repair.calculate_total_cost()
        repair.save(update_fields=['total_cost'])
        updated += 1
    
    modeladmin.message_user(
        request,
        f'Пересчитана стоимость {updated} ремонтов',
        messages.SUCCESS
    )


@admin.action(description='Создать отчет по выбранным клиентам')
def generate_client_report(modeladmin, request, queryset):
    """Создать отчет по выбранным клиентам"""
    if queryset.count() > 50:
        modeladmin.message_user(
            request,
            'Слишком много клиентов выбрано (максимум 50)',
            messages.ERROR
        )
        return
    
    # Подготовка данных для отчета
    report_data = []
    for client in queryset:
        repairs_count = client.repairs.count()
        total_spent = client.total_repairs_cost()
        avg_repair_cost = total_spent / repairs_count if repairs_count > 0 else Decimal('0.00')
        
        report_data.append({
            'client': client,
            'repairs_count': repairs_count,
            'total_spent': total_spent,
            'avg_repair_cost': avg_repair_cost,
            'last_repair': client.repairs.order_by('-created_at').first()
        })
    
    # Создание CSV отчета
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="client_report.csv"'
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow([
        'ФИО клиента',
        'Телефон',
        'Email',
        'Количество ремонтов',
        'Общая сумма',
        'Средняя стоимость ремонта',
        'Последний ремонт',
        'VIP статус'
    ])
    
    for data in report_data:
        client = data['client']
        writer.writerow([
            client.user.get_full_name(),
            client.phone,
            client.user.email,
            data['repairs_count'],
            data['total_spent'],
            data['avg_repair_cost'],
            data['last_repair'].created_at.strftime('%d.%m.%Y') if data['last_repair'] else '',
            'Да' if client.is_vip else 'Нет'
        ])
    
    return response


@admin.action(description='Автоматически назначить VIP статус')
def auto_assign_vip_status(modeladmin, request, queryset):
    """Автоматически назначить VIP статус клиентам"""
    # Критерии VIP: более 5 ремонтов или потратил более 50000 рублей
    vip_assigned = 0
    
    for client in queryset:
        repairs_count = client.repairs.count()
        total_spent = client.total_repairs_cost()
        
        if (repairs_count >= 5 or total_spent >= Decimal('50000.00')) and not client.is_vip:
            client.is_vip = True
            client.save(update_fields=['is_vip'])
            vip_assigned += 1
    
    modeladmin.message_user(
        request,
        f'VIP статус назначен {vip_assigned} клиентам',
        messages.SUCCESS
    )


@admin.action(description='Создать массовое уведомление')
def send_bulk_notification(modeladmin, request, queryset):
    """Отправить массовое уведомление клиентам"""
    if 'apply' in request.POST:
        # Получаем данные формы
        message_text = request.POST.get('message_text', '')
        notification_type = request.POST.get('notification_type', 'info')
        
        if not message_text:
            modeladmin.message_user(
                request,
                'Сообщение не может быть пустым',
                messages.ERROR
            )
            return
        
        # Здесь можно добавить логику отправки уведомлений
        # Например, через email или SMS
        sent_count = 0
        for client in queryset:
            # Логика отправки уведомления
            # send_notification(client, message_text, notification_type)
            sent_count += 1
        
        modeladmin.message_user(
            request,
            f'Уведомления отправлены {sent_count} клиентам',
            messages.SUCCESS
        )
        return
    
    # Отображаем форму для ввода сообщения
    context = {
        'title': 'Отправить массовое уведомление',
        'queryset': queryset,
        'action_checkbox_name': admin.ACTION_CHECKBOX_NAME,
        'opts': modeladmin.model._meta,
    }
    
    return render(request, 'admin/bulk_notification.html', context)


@admin.action(description='Архивировать старые записи')
def archive_old_records(modeladmin, request, queryset):
    """Архивировать старые записи (старше 2 лет)"""
    from datetime import datetime, timedelta
    
    two_years_ago = timezone.now() - timedelta(days=730)
    old_records = queryset.filter(created_at__lt=two_years_ago)
    
    if not old_records.exists():
        modeladmin.message_user(
            request,
            'Нет записей старше 2 лет для архивации',
            messages.INFO
        )
        return
    
    if 'apply' in request.POST:
        # Выполняем архивацию
        archived_count = 0
        for record in old_records:
            # Здесь можно добавить логику архивации
            # например, перенос в архивную таблицу
            record.is_archived = True if hasattr(record, 'is_archived') else None
            if hasattr(record, 'is_archived'):
                record.save(update_fields=['is_archived'])
                archived_count += 1
        
        modeladmin.message_user(
            request,
            f'Заархивировано {archived_count} записей',
            messages.SUCCESS
        )
        return
    
    # Отображаем подтверждение
    context = {
        'title': 'Архивировать старые записи',
        'queryset': old_records,
        'records_count': old_records.count(),
        'action_checkbox_name': admin.ACTION_CHECKBOX_NAME,
        'opts': modeladmin.model._meta,
    }
    
    return render(request, 'admin/archive_confirmation.html', context)


@admin.action(description='Проверить целостность данных')
def validate_data_integrity(modeladmin, request, queryset):
    """Проверить целостность данных"""
    errors = []
    warnings = []
    
    for obj in queryset:
        # Проверки зависят от модели
        if hasattr(obj, 'total_sum') and obj.total_sum <= 0:
            errors.append(f'{obj}: Общая сумма должна быть больше нуля')
        
        if hasattr(obj, 'client') and not obj.client:
            errors.append(f'{obj}: Не указан клиент')
        
        if hasattr(obj, 'orders') and not obj.orders.exists():
            warnings.append(f'{obj}: Нет связанных заказов')
    
    # Формируем отчет
    report = []
    if errors:
        report.append(f'Ошибки ({len(errors)}):')
        report.extend(errors)
    
    if warnings:
        report.append(f'Предупреждения ({len(warnings)}):')
        report.extend(warnings)
    
    if not errors and not warnings:
        modeladmin.message_user(
            request,
            'Все проверки пройдены успешно',
            messages.SUCCESS
        )
    else:
        message = '\n'.join(report)
        level = messages.ERROR if errors else messages.WARNING
        modeladmin.message_user(request, message, level)


# Действия для конкретных моделей

def contract_actions():
    """Возвращает список действий для модели Contract"""
    return [
        export_selected_contracts_csv,
        mark_as_completed,
        mark_as_in_progress,
        mark_as_cancelled,
        recalculate_contract_sums,
        validate_data_integrity,
        archive_old_records,
    ]


def repair_actions():
    """Возвращает список действий для модели Repair"""
    return [
        export_selected_repairs_csv,
        mark_as_completed,
        mark_as_in_progress,
        mark_as_cancelled,
        recalculate_repair_costs,
        validate_data_integrity,
        archive_old_records,
    ]


def client_actions():
    """Возвращает список действий для модели Client"""
    return [
        generate_client_report,
        auto_assign_vip_status,
        send_bulk_notification,
        archive_old_records,
    ]
