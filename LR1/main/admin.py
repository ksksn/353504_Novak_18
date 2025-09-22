from django.contrib import admin
from django.db.models import Sum, Count, Q, F, Avg
from django.utils.html import format_html
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import path, reverse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
import csv

from .models import (
    Client, Device, DeviceType, SparePart, Repair, RepairSparePart,
    Service, Employee, Order, Contract, ServiceType, EmployeeSpecialization, 
    Part, PartType, FAQ, JobVacancy, Cart, CartItem, ServiceRequest, ServiceRequestItem
)

# === КАСТОМНЫЙ АДМИН-САЙТ ===
class ServiceCenterAdminSite(admin.AdminSite):
    site_header = 'Админ-панель сервисного центра'
    site_title = 'Сервисный центр'
    index_title = 'Управление сервисным центром'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reports/', self.admin_view(reports_dashboard), name='reports_dashboard'),
            path('contract/<int:contract_id>/print/', self.admin_view(contract_print_view), name='contract_print'),
            path('api/client/<int:client_id>/devices/', self.admin_view(api_client_devices), name='api_client_devices'),
        ]
        return custom_urls + urls

# === УТИЛИТЫ ===
def format_money(amount):
    if amount is None:
        return "0.00 руб."
    return f"{amount:.2f} руб."

def get_status_badge(status):
    colors = {
        'pending': 'warning',
        'in_progress': 'info', 
        'completed': 'success',
        'cancelled': 'danger',
    }
    color = colors.get(status, 'secondary')
    return format_html('<span class="badge badge-{}">{}</span>', color, status)

# === ДЕЙСТВИЯ ===
@admin.action(description='Пересчитать стоимость')
def recalculate_costs(modeladmin, request, queryset):
    updated = 0
    for obj in queryset:
        if hasattr(obj, 'calculate_total_cost'):
            obj.calculate_total_cost()
            obj.save()
            updated += 1
    modeladmin.message_user(request, f'Пересчитано {updated} объектов.')

@admin.action(description='Отметить как завершенные')
def mark_completed(modeladmin, request, queryset):
    updated = queryset.update(status='completed')
    modeladmin.message_user(request, f'Отмечено завершенными {updated} объектов.')

@admin.action(description='Экспорт в CSV')
def export_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{modeladmin.model._meta.model_name}.csv"'
    response.write('\ufeff')
    
    writer = csv.writer(response)
    if hasattr(queryset.first(), 'user'):
        writer.writerow(['ФИО', 'Телефон', 'Email', 'Дата регистрации'])
        for obj in queryset:
            writer.writerow([obj.user.get_full_name(), obj.phone, obj.user.email, obj.registration_date])
    else:
        writer.writerow(['ID', 'Название', 'Дата создания'])
        for obj in queryset:
            writer.writerow([obj.id, str(obj), getattr(obj, 'created_at', '')])
    
    return response

# === ИНЛАЙНЫ ===
class RepairSparePartInline(admin.TabularInline):
    model = RepairSparePart
    extra = 1
    fields = ['spare_part', 'quantity', 'total_price_display']
    readonly_fields = ['total_price_display']
    
    def total_price_display(self, obj):
        if obj.spare_part and obj.quantity:
            return format_money(obj.spare_part.price * obj.quantity)
        return "—"
    total_price_display.short_description = "Стоимость"

class OrderInline(admin.TabularInline):
    model = Order
    extra = 1
    fields = ['service', 'device', 'quantity', 'status']
    readonly_fields = ['total_sum']

class ServiceRequestItemInline(admin.TabularInline):
    model = ServiceRequestItem
    extra = 0
    readonly_fields = ['total_price']

# === ОСНОВНЫЕ АДМИН-КЛАССЫ ===
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['user_full_name', 'phone', 'is_vip', 'total_repairs', 'total_spent_display']
    list_filter = ['is_vip', 'registration_date']
    search_fields = ['user__first_name', 'user__last_name', 'phone', 'user__email']
    readonly_fields = ['registration_date']
    actions = [export_csv]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'phone', 'address', 'birth_date', 'is_vip')
        }),
        ('Системная информация', {
            'fields': ('registration_date',),
            'classes': ('collapse',)
        }),
    )

    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = "ФИО"

    def total_repairs(self, obj):
        return obj.repairs.count()
    total_repairs.short_description = "Ремонтов"

    def total_spent_display(self, obj):
        total = obj.total_repairs_cost() if hasattr(obj, 'total_repairs_cost') else 0
        return format_money(total)
    total_spent_display.short_description = "Потрачено"

@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_name', 'device', 'status', 'total_cost_display', 'created_at']
    list_filter = ['status', 'created_at', 'device__device_type']
    search_fields = ['client__user__first_name', 'client__user__last_name', 'device__name']
    inlines = [RepairSparePartInline]
    readonly_fields = ['created_at', 'total_cost']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    actions = [recalculate_costs, mark_completed, export_csv]
    
    def client_name(self, obj):
        return obj.client.user.get_full_name()
    client_name.short_description = "Клиент"

    def total_cost_display(self, obj):
        return format_money(obj.total_cost)
    total_cost_display.short_description = "Стоимость"

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['number', 'client_name', 'employee', 'date_signed', 'total_sum_display', 'is_completed']
    list_filter = ['is_completed', 'date_signed', 'employee']
    search_fields = ['number', 'client__user__first_name', 'client__user__last_name']
    inlines = [OrderInline]
    readonly_fields = ['created_at', 'updated_at', 'total_sum']
    actions = [mark_completed, export_csv]
    
    def client_name(self, obj):
        return obj.client.user.get_full_name()
    client_name.short_description = "Клиент"

    def total_sum_display(self, obj):
        return format_money(obj.total_sum)
    total_sum_display.short_description = "Сумма"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'contract_number', 'service', 'device', 'status', 'total_sum_display']
    list_filter = ['status', 'service__service_type']
    search_fields = ['contract__number', 'service__name']
    list_editable = ['status']
    actions = [mark_completed, export_csv]
    
    def contract_number(self, obj):
        return obj.contract.number
    contract_number.short_description = "Договор"

    def total_sum_display(self, obj):
        return format_money(obj.total_sum)
    total_sum_display.short_description = "Сумма"

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_type', 'model', 'serial_number', 'client_name']
    list_filter = ['device_type']
    search_fields = ['name', 'model', 'serial_number']
    actions = [export_csv]
    
    def client_name(self, obj):
        return obj.client.user.get_full_name() if obj.client else "—"
    client_name.short_description = "Владелец"

@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'quantity_in_stock', 'stock_status']
    list_filter = ['category']
    search_fields = ['name', 'category']
    list_editable = ['price', 'quantity_in_stock']
    actions = [export_csv]
    
    def stock_status(self, obj):
        if obj.quantity_in_stock == 0:
            return format_html('<span style="color: red;">Нет в наличии</span>')
        elif obj.quantity_in_stock < 5:
            return format_html('<span style="color: orange;">Мало ({})</span>', obj.quantity_in_stock)
        else:
            return format_html('<span style="color: green;">В наличии ({})</span>', obj.quantity_in_stock)
    stock_status.short_description = "Статус"

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'price', 'is_active']
    list_filter = ['service_type', 'is_active']
    search_fields = ['name']
    list_editable = ['price', 'is_active']

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'position', 'phone', 'hire_date']
    list_filter = ['position', 'hire_date']
    search_fields = ['user__first_name', 'user__last_name']
    filter_horizontal = ['specializations']
    
    def user_name(self, obj):
        return obj.user.get_full_name()
    user_name.short_description = "ФИО"

# === ПРОСТЫЕ МОДЕЛИ ===
admin.site.register(EmployeeSpecialization)
admin.site.register(FAQ)
admin.site.register(JobVacancy)
admin.site.register(Part)
admin.site.register(PartType)
admin.site.register(RepairSparePart)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ServiceRequest)
admin.site.register(ServiceRequestItem)

# === КАСТОМНЫЕ ПРЕДСТАВЛЕНИЯ ===
@staff_member_required
def reports_dashboard(request):
    """Страница отчетов"""
    # Общая статистика
    total_repairs = Repair.objects.count()
    total_clients = Client.objects.count()
    total_revenue = Contract.objects.filter(is_completed=True).aggregate(
        total=Sum('total_sum'))['total'] or 0
    
    # Статистика по месяцам
    monthly_stats = Repair.objects.filter(
        created_at__year=datetime.now().year
    ).extra(
        select={'month': "strftime('%%m', created_at)"}
    ).values('month').annotate(
        count=Count('id'),
        revenue=Sum('total_cost')
    ).order_by('month')
    
    # Топ клиенты
    top_clients = Client.objects.annotate(
        total_spent=Sum('repairs__total_cost')
    ).order_by('-total_spent')[:10]
    
    context = {
        'title': 'Отчеты и статистика',
        'total_repairs': total_repairs,
        'total_clients': total_clients,
        'total_revenue': total_revenue,
        'monthly_stats': monthly_stats,
        'top_clients': top_clients,
    }
    
    return render(request, 'admin/reports_dashboard.html', context)

@staff_member_required
def contract_print_view(request, contract_id):
    """Печать договора"""
    contract = get_object_or_404(Contract, pk=contract_id)
    html = render_to_string('admin/contract_print.html', {'contract': contract})
    return HttpResponse(html)

@staff_member_required
def api_client_devices(request, client_id):
    """API для получения устройств клиента"""
    devices = Device.objects.filter(client_id=client_id).values('id', 'name', 'model')
    return JsonResponse({'devices': list(devices)})

# === НАСТРОЙКА АДМИН-ПАНЕЛИ ===
admin.site.site_header = 'Админ-панель сервисного центра'
admin.site.site_title = 'Сервисный центр'
admin.site.index_title = 'Управление сервисным центром'
