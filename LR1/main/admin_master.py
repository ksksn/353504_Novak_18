from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from django.shortcuts import render
from datetime import date, datetime
from .models import (
    Client, Device, Service, Order, Repair, RepairSparePart, ServiceRequest
)

class MasterAdminSite(admin.AdminSite):
    site_header = "Панель мастера сервисного центра"
    site_title = "Сервисный центр - Мастер"
    index_title = "Управление заказами и ремонтами"
    
    def has_permission(self, request):
        """
        Проверяет, имеет ли пользователь доступ к этому административному сайту.
        Разрешает доступ только для мастеров (пользователи из группы 'Master').
        """
        return request.user.is_active and (
            request.user.is_staff or 
            request.user.groups.filter(name='Master').exists()
        )

# Создаем сайт администрирования для мастеров
master_admin_site = MasterAdminSite(name='master_admin')

# === Инлайн-модели для мастера ===

class RepairSparePartInline(admin.TabularInline):
    model = RepairSparePart
    extra = 1
    fields = ['spare_part', 'quantity', 'total_price_display']
    readonly_fields = ['total_price_display']
    
    def total_price_display(self, obj):
        if obj.spare_part and obj.quantity:
            return f"{obj.spare_part.price * obj.quantity:.2f} руб."
        return "—"
    total_price_display.short_description = "Стоимость"

# === Модели для мастера ===

@admin.register(Repair, site=master_admin_site)
class MasterRepairAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_display', 'device', 'status', 'created_at', 'total_cost']
    list_filter = ['status', 'created_at']
    search_fields = ['client__user__first_name', 'client__user__last_name', 'device__name']
    readonly_fields = ['client', 'device', 'created_at', 'total_cost']
    inlines = [RepairSparePartInline]
    
    fieldsets = (
        ('Информация о ремонте', {
            'fields': ('client', 'device', 'description', 'status')
        }),
        ('Стоимость', {
            'fields': ('labor_cost', 'total_cost'),
        }),
        ('Системная информация', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def client_display(self, obj):
        return f"{obj.client.user.get_full_name()}"
    client_display.short_description = "Клиент"
    
    def get_queryset(self, request):
        """
        Мастер видит только ремонты, назначенные ему через расписание,
        либо ремонты устройств клиентов, записанных к нему.
        """
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            try:
                master = request.user.employee
                # Показываем ремонты, которые может выполнять этот мастер
                # (пока без расписания - показываем все)
                return qs
            except:
                return qs.none()
        return qs
    
    def has_add_permission(self, request):
        # Мастер не может добавлять ремонты
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Мастер не может удалять ремонты
        return False

# Schedule модель недоступна - закомментировано
# Schedule модель недоступна - закомментировано
# @admin.register(Schedule, site=master_admin_site)
# class MasterScheduleAdmin(admin.ModelAdmin):
#     list_display = ['date', 'time_start', 'time_end', 'client_display', 'service', 'is_booked']
#     list_filter = ['date', 'is_booked']
#     search_fields = ['client__user__first_name', 'client__user__last_name']
#     readonly_fields = ['employee']
#     
#     def client_display(self, obj):
#         return obj.client.user.get_full_name() if obj.client else "—"
#     client_display.short_description = "Клиент"
#     
#     def get_queryset(self, request):
#         """
#         Мастер видит только своё расписание
#         """
#         qs = super().get_queryset(request)
#         if not request.user.is_superuser:
#             try:
#                 master = request.user.employee
#                 return qs.filter(employee=master)
#             except:
#                 return qs.none()
#         return qs
#     
#     def has_add_permission(self, request):
#         # Мастер не может добавлять расписание
#         return False
#     
#     def has_delete_permission(self, request, obj=None):
#         # Мастер не может удалять расписание
#         return False
#     
#     def save_model(self, request, obj, form, change):
#         """
#         При сохранении автоматически устанавливаем сотрудника
#         равным текущему пользователю-мастеру
#         """
#         if not obj.employee and hasattr(request.user, 'employee'):
#             obj.employee = request.user.employee
#         super().save_model(request, obj, form, change)

@admin.register(Client, site=master_admin_site)
class MasterClientAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'repairs_count']
    search_fields = ['user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['user', 'phone', 'address', 'birth_date', 'registration_date', 'is_vip']
    
    fieldsets = (
        ('Личная информация', {
            'fields': ('user', 'phone', 'address', 'is_vip')
        }),
    )
    
    def repairs_count(self, obj):
        return obj.repairs.count()
    repairs_count.short_description = "Всего ремонтов"
    
    def get_queryset(self, request):
        """
        Мастер видит только клиентов из своего расписания
        """
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            try:
                master = request.user.employee
                # Показываем всех клиентов (пока без расписания)
                return qs
            except:
                return qs.none()
        return qs
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

# Регистрируем дополнительные модели только для чтения

@admin.register(Order, site=master_admin_site)
class MasterOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_name', 'service', 'device', 'status']
    search_fields = ['contract__client__user__first_name', 'contract__client__user__last_name']
    readonly_fields = ['contract', 'service', 'device', 'quantity', 'status', 'total_sum']
    
    def client_name(self, obj):
        return obj.contract.client.user.get_full_name()
    client_name.short_description = "Клиент"
    
    def get_queryset(self, request):
        """
        Мастер видит только заказы клиентов из своего расписания
        """
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            try:
                master = request.user.employee
                # Показываем все заказы (пока без расписания)
                return qs
            except:
                return qs.none()
        return qs
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Device, site=master_admin_site)
class MasterDeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_type', 'model', 'client_name']
    search_fields = ['name', 'model', 'client__user__first_name', 'client__user__last_name']
    readonly_fields = ['name', 'device_type', 'model', 'serial_number', 'client']
    
    def client_name(self, obj):
        return obj.client.user.get_full_name() if obj.client else "—"
    client_name.short_description = "Клиент"
    
    def get_queryset(self, request):
        """
        Мастер видит только устройства клиентов из своего расписания
        """
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            try:
                master = request.user.employee
                # Показываем все устройства (пока без расписания)
                return qs
            except:
                return qs.none()
        return qs
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False 