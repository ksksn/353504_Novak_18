from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db import models
from django.db.models import Sum, Count
from django.utils.html import format_html
from .models import (
    Client, Device, DeviceType, Part, PartType, Repair, RepairSparePart,
    Service, Employee, Order, Contract,
    EmployeeSpecialization, ServiceType, SparePart, FAQ, JobVacancy,
    Cart, CartItem, ServiceRequest, ServiceRequestItem
)


class ServiceCenterAdminSite(AdminSite):
    site_header = "Административная панель сервисного центра"
    site_title = "Сервисный центр"
    index_title = "Управление сервисным центром"
    
    def get_urls(self):
        """Добавляем кастомные URL для отчетов"""
        from django.urls import path
        from . import admin_reports
        
        urls = super().get_urls()
        custom_urls = [
            path('reports/', admin_reports.reports_dashboard, name='reports_dashboard'),
            path('reports/financial/', admin_reports.financial_report, name='financial_report'),
            path('reports/clients/', admin_reports.client_analytics, name='client_analytics'),
            path('reports/parts/', admin_reports.parts_analytics, name='parts_analytics'),
            path('reports/export-contracts/', admin_reports.export_contracts_csv, name='export_contracts_csv'),
            path('api/contract-stats/', admin_reports.api_contract_stats, name='api_contract_stats'),
        ]
        return custom_urls + urls
    
    def get_app_list(self, request, app_label=None):
        """
        Кастомная группировка моделей в админке
        """
        app_list = super().get_app_list(request, app_label)
        
        # Убираем стандартную группировку и создаем свою
        custom_groups = {
            'Основные операции': [
                'main.repair',
                'main.contract', 
                'main.order',
                'main.client',
            ],
            'Устройства и запчасти': [
                'main.device',
                'main.devicetype',
                'main.sparepart',
                'main.parttype',
            ],
            'Услуги и сотрудники': [
                'main.service',
                'main.servicetype', 
                'main.employee',
                'main.employeespecialization',
            ],
            'Отчеты и аналитика': [
                {'name': 'Общие отчеты', 'admin_url': '/admin/reports/', 'add_url': None, 'change_url': None},
                {'name': 'Финансовый отчет', 'admin_url': '/admin/reports/financial/', 'add_url': None, 'change_url': None},
                {'name': 'Аналитика клиентов', 'admin_url': '/admin/reports/clients/', 'add_url': None, 'change_url': None},
                {'name': 'Аналитика запчастей', 'admin_url': '/admin/reports/parts/', 'add_url': None, 'change_url': None},
                {'name': 'Экспорт договоров', 'admin_url': '/admin/reports/export-contracts/', 'add_url': None, 'change_url': None},
            ],
            'Контент и отзывы': [
                'main.news',
                'main.category',
                'main.tag',
                'main.review',
                'main.term',
            ],
            'Настройки': [
                'main.companyinfo',
                'main.schedule',
                'main.promocode',
                'main.vacancy',
                'main.passportdata',
            ],
        }
        
        new_app_list = []
        
        for group_name, model_names in custom_groups.items():
            group_models = []
            
            if group_name == 'Отчеты и аналитика':
                # Добавляем кастомные ссылки для отчетов
                for report in model_names:
                    group_models.append({
                        'name': report['name'],
                        'object_name': report['name'].lower().replace(' ', '_'),
                        'admin_url': report['admin_url'],
                        'add_url': report['add_url'],
                        'change_url': report['change_url'],
                        'view_only': True,
                    })
            else:
                # Обычные модели
                for app in app_list:
                    if app['app_label'] == 'main':
                        for model in app['models']:
                            model_key = f"main.{model['object_name'].lower()}"
                            if model_key in model_names:
                                group_models.append(model)
            
            if group_models:
                new_app_list.append({
                    'name': group_name,
                    'app_label': f'group_{group_name.lower().replace(" ", "_")}',
                    'models': group_models
                })
        
        # Добавляем встроенные приложения Django
        for app in app_list:
            if app['app_label'] in ['auth', 'contenttypes', 'sessions', 'admin']:
                new_app_list.append(app)
        
        return new_app_list


# Создаем кастомный сайт админки
admin_site = ServiceCenterAdminSite(name='service_center_admin')

# Инлайны
class RepairSparePartInline(admin.TabularInline):
    model = RepairSparePart
    extra = 1
    fields = ['spare_part', 'quantity']
    autocomplete_fields = ['spare_part']

class OrderInline(admin.TabularInline):
    model = Order
    extra = 1
    fields = ['service', 'device', 'quantity', 'status']
    autocomplete_fields = ['service', 'device']
    readonly_fields = ['total_sum']


# === ОСНОВНЫЕ ОПЕРАЦИИ ===

@admin.register(Client, site=admin_site)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'user_email', 'registration_date', 'total_repairs_cost_display']
    list_filter = ['registration_date', 'is_vip']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
    readonly_fields = ['registration_date']
    
    # Отчеты
    change_list_template = 'admin/repair_report.html'

    def full_name(self, obj):
        return obj.user.get_full_name()
    full_name.short_description = 'ФИО'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def total_repairs_cost_display(self, obj):
        return f"{obj.total_repairs_cost():.2f} руб."
    total_repairs_cost_display.short_description = "Общая сумма ремонтов"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        
        # Статистика по годам
        yearly_stats = Repair.objects.extra(
            select={'year': 'EXTRACT(year FROM created_at)'}
        ).values('year').annotate(
            total_repairs=models.Count('id'),
            total_revenue=Sum('total_cost')
        ).order_by('-year')
        
        # Статистика по клиентам
        client_stats = Client.objects.annotate(
            total_spent=Sum('repairs__total_cost'),
            repairs_count=Count('repairs')
        ).order_by('-total_spent')[:10]
        
        # Популярные запчасти
        popular_parts = SparePart.objects.annotate(
            usage_count=Sum('repairsparepart__quantity')
        ).order_by('-usage_count')[:10]
        
        # Статистика по договорам
        contract_stats = Contract.objects.annotate(
            orders_count=Count('order'),
            total_value=Sum('total_sum')
        ).order_by('-total_value')[:10]
        
        extra_context = extra_context or {}
        extra_context.update({
            'yearly_stats': yearly_stats,
            'client_stats': client_stats,
            'popular_parts': popular_parts,
            'contract_stats': contract_stats,
            'title': 'Отчеты по ремонтам и договорам',
        })
        
        if hasattr(response, 'context_data'):
            response.context_data.update(extra_context)
        
        return response

@admin.register(Repair, site=admin_site)
class RepairAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'device', 'status', 'labor_cost', 'total_cost_display', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at', 'device__device_type']
    search_fields = ['client__user__first_name', 'client__user__last_name', 'device__name', 'device__model', 'description']
    inlines = [RepairSparePartInline]
    readonly_fields = ['created_at', 'total_cost']
    exclude = ['updated_at']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['client', 'device']

    def total_cost_display(self, obj):
        return f"{obj.total_cost:.2f} руб."
    total_cost_display.short_description = "Общая стоимость"

    def save_model(self, request, obj, form, change):
        obj.calculate_total_cost()
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.calculate_total_cost()
        form.instance.save()

@admin.register(Contract, site=admin_site)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['number', 'client', 'employee', 'date_signed', 'deadline', 'services_count', 'completion_percentage', 'total_sum_display', 'is_completed']
    list_filter = ['is_completed', 'date_signed', 'deadline', 'employee']
    search_fields = ['number', 'client__user__first_name', 'client__user__last_name']
    inlines = [OrderInline]
    readonly_fields = ['created_at', 'updated_at', 'total_sum', 'services_breakdown_display']
    exclude = []
    autocomplete_fields = ['client', 'employee']
    list_editable = ['is_completed']
    date_hierarchy = 'date_signed'
    actions = ['recalculate_totals', 'mark_completed', 'generate_contract_report']

    fieldsets = (
        ('Основная информация', {
            'fields': ('number', 'client', 'employee', 'date_signed', 'deadline', 'is_completed')
        }),
        ('Финансовая информация', {
            'fields': ('total_sum',),
            'description': 'Итоговая сумма рассчитывается автоматически на основе заказов'
        }),
        ('Детализация услуг', {
            'fields': ('services_breakdown_display',),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_sum_display(self, obj):
        return f"{obj.total_sum:.2f} руб."
    total_sum_display.short_description = "Итоговая сумма"
    
    def services_count(self, obj):
        return obj.get_services_count()
    services_count.short_description = "Количество услуг"
    
    def completion_percentage(self, obj):
        percentage = obj.get_completion_status()
        if percentage == 100:
            return format_html('<span style="color: green; font-weight: bold;">{}%</span>', percentage)
        elif percentage >= 50:
            return format_html('<span style="color: orange;">{}%</span>', percentage)
        else:
            return format_html('<span style="color: red;">{}%</span>', percentage)
    completion_percentage.short_description = "Выполнение"
    
    def services_breakdown_display(self, obj):
        breakdown = obj.get_services_breakdown()
        if not breakdown:
            return "Нет услуг"
        
        html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        html += "<tr><th>Услуга</th><th>Устройство</th><th>Кол-во</th><th>Услуги</th><th>Запчасти</th><th>Итого</th><th>Статус</th></tr>"
        
        for item in breakdown:
            html += f"<tr>"
            html += f"<td>{item['service']}</td>"
            html += f"<td>{item['device']}</td>"
            html += f"<td>{item['quantity']}</td>"
            html += f"<td>{item['service_cost']:.2f} руб.</td>"
            html += f"<td>{item['parts_cost']:.2f} руб.</td>"
            html += f"<td><strong>{item['total_cost']:.2f} руб.</strong></td>"
            html += f"<td>{item['status']}</td>"
            html += f"</tr>"
        
        html += "</table>"
        return format_html(html)
    services_breakdown_display.short_description = "Детализация услуг"
    
    def recalculate_totals(self, request, queryset):
        """Пересчитать итоговые суммы договоров"""
        updated = 0
        for contract in queryset:
            contract.calculate_total_sum()
            updated += 1
        self.message_user(request, f'Пересчитаны суммы для {updated} договоров.')
    recalculate_totals.short_description = "Пересчитать итоговые суммы"
    
    def mark_completed(self, request, queryset):
        """Отметить договоры как выполненные"""
        updated = queryset.update(is_completed=True)
        self.message_user(request, f'Отмечено как выполненные {updated} договоров.')
    mark_completed.short_description = "Отметить как выполненные"
    
    def generate_contract_report(self, request, queryset):
        """Генерация отчета по выбранным договорам"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="contracts_report.csv"'
        response.write('\ufeff')  # BOM для корректного отображения кириллицы в Excel
        
        writer = csv.writer(response)
        writer.writerow(['Номер договора', 'Клиент', 'Сотрудник', 'Дата заключения', 
                        'Срок выполнения', 'Количество услуг', 'Стоимость услуг', 
                        'Стоимость запчастей', 'Итоговая сумма', 'Выполнение %', 'Статус'])
        
        for contract in queryset:
            writer.writerow([
                contract.number,
                contract.client.user.get_full_name(),
                contract.employee.user.get_full_name() if contract.employee else 'Не назначен',
                contract.date_signed.strftime('%d.%m.%Y'),
                contract.deadline.strftime('%d.%m.%Y'),
                contract.get_services_count(),
                f"{contract.get_total_services_cost():.2f}",
                f"{contract.get_total_parts_cost():.2f}",
                f"{contract.total_sum:.2f}",
                f"{contract.get_completion_status():.1f}%",
                'Выполнен' if contract.is_completed else 'В работе'
            ])
        
        return response
    generate_contract_report.short_description = "Экспорт отчета в CSV"

@admin.register(Order, site=admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'contract_link', 'service', 'device', 'quantity', 'service_sum', 'parts_sum', 'total_sum_display', 'status']
    list_filter = ['status', 'service__service_type', 'created_at']
    search_fields = ['contract__number', 'service__name', 'device__name', 'contract__client__user__first_name', 'contract__client__user__last_name']
    autocomplete_fields = ['contract', 'service', 'device']
    filter_horizontal = ['parts']
    exclude = ['created_at', 'updated_at']
    list_editable = ['status']
    readonly_fields = ['service_sum', 'parts_sum', 'total_sum', 'parts_list_display']
    actions = ['recalculate_order_sums', 'mark_completed', 'mark_in_progress']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('contract', 'service', 'device', 'quantity', 'status')
        }),
        ('Стоимость', {
            'fields': ('service_sum', 'parts_sum', 'total_sum'),
            'description': 'Стоимость рассчитывается автоматически'
        }),
        ('Запчасти', {
            'fields': ('parts', 'parts_list_display'),
            'description': 'Выберите необходимые запчасти'
        }),
    )

    def total_sum_display(self, obj):
        return f"{obj.total_sum:.2f} руб."
    total_sum_display.short_description = "Итоговая сумма"
    
    def contract_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:main_contract_change', args=[obj.contract.pk])
        return format_html('<a href="{}">{}</a>', url, obj.contract.number)
    contract_link.short_description = "Договор"
    
    def parts_list_display(self, obj):
        parts = obj.parts.all()
        if not parts:
            return "Нет запчастей"
        
        parts_info = []
        for part in parts:
            parts_info.append(f"{part.name} ({part.price:.2f} руб.)")
        return "; ".join(parts_info)
    parts_list_display.short_description = "Список запчастей"
    
    def recalculate_order_sums(self, request, queryset):
        """Пересчитать суммы заказов"""
        updated = 0
        for order in queryset:
            order.calculate_sums()
            order.save()
            if order.contract:
                order.contract.calculate_total_sum()
            updated += 1
        self.message_user(request, f'Пересчитаны суммы для {updated} заказов.')
    recalculate_order_sums.short_description = "Пересчитать суммы заказов"
    
    def mark_completed(self, request, queryset):
        """Отметить заказы как завершенные"""
        updated = queryset.update(status='completed')
        # Обновляем суммы договоров
        for order in queryset:
            if order.contract:
                order.contract.calculate_total_sum()
        self.message_user(request, f'Отмечено как завершенные {updated} заказов.')
    mark_completed.short_description = "Отметить как завершенные"
    
    def mark_in_progress(self, request, queryset):
        """Отметить заказы как в работе"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'Отмечено как в работе {updated} заказов.')
    mark_in_progress.short_description = "Отметить как в работе"


# === УСТРОЙСТВА И ЗАПЧАСТИ ===

@admin.register(Device, site=admin_site)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_type', 'model', 'serial_number', 'client', 'repairs_count']
    list_filter = ['device_type', 'client']
    search_fields = ['name', 'model', 'serial_number', 'client__user__first_name', 'client__user__last_name']
    autocomplete_fields = ['client']

    def repairs_count(self, obj):
        return obj.repair_set.count()
    repairs_count.short_description = "Количество ремонтов"

@admin.register(DeviceType, site=admin_site)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'devices_count']
    search_fields = ['name']

    def devices_count(self, obj):
        return obj.device_set.count()
    devices_count.short_description = "Количество устройств"

@admin.register(SparePart, site=admin_site)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'quantity_in_stock', 'stock_status', 'usage_count']
    list_filter = ['category', 'quantity_in_stock']
    search_fields = ['name', 'category']
    list_editable = ['price', 'quantity_in_stock']
    filter_horizontal = ['compatible_devices']
    actions = ['update_stock', 'mark_low_stock', 'generate_parts_report']

    def stock_status(self, obj):
        if obj.quantity_in_stock == 0:
            return format_html('<span style="color: red; font-weight: bold;">Нет в наличии</span>')
        elif obj.quantity_in_stock < 5:
            return format_html('<span style="color: orange; font-weight: bold;">Мало ({})</span>', obj.quantity_in_stock)
        else:
            return format_html('<span style="color: green;">В наличии ({})</span>', obj.quantity_in_stock)
    stock_status.short_description = "Статус склада"
    
    def usage_count(self, obj):
        """Показать количество использований запчасти"""
        count = obj.repairsparepart_set.aggregate(total=Sum('quantity'))['total'] or 0
        return count
    usage_count.short_description = "Использовано"
    
    def update_stock(self, request, queryset):
        """Обновить количество на складе"""
        # Здесь можно добавить форму для массового обновления
        self.message_user(request, 'Выберите запчасти для обновления количества')
    update_stock.short_description = "Обновить количество на складе"
    
    def mark_low_stock(self, request, queryset):
        """Отметить запчасти с низким остатком"""
        low_stock = queryset.filter(quantity_in_stock__lt=5)
        count = low_stock.count()
        self.message_user(request, f'Найдено {count} запчастей с низким остатком')
    mark_low_stock.short_description = "Найти запчасти с низким остатком"
    
    def generate_parts_report(self, request, queryset):
        """Генерация отчета по запчастям"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="parts_report.csv"'
        response.write('\ufeff')
        
        writer = csv.writer(response)
        writer.writerow(['Название', 'Категория', 'Цена', 'На складе', 'Использовано', 'Статус'])
        
        for part in queryset:
            usage = part.repairsparepart_set.aggregate(total=Sum('quantity'))['total'] or 0
            status = 'Нет в наличии' if part.quantity_in_stock == 0 else ('Мало' if part.quantity_in_stock < 5 else 'В наличии')
            
            writer.writerow([
                part.name,
                part.category,
                f"{part.price:.2f}",
                part.quantity_in_stock,
                usage,
                status
            ])
        
        return response
    generate_parts_report.short_description = "Экспорт отчета по запчастям"

@admin.register(PartType, site=admin_site)
class PartTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'parts_count']
    search_fields = ['name']

    def parts_count(self, obj):
        return obj.part_set.count()
    parts_count.short_description = "Количество запчастей"


# === УСЛУГИ И СОТРУДНИКИ ===

@admin.register(Service, site=admin_site)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'price', 'is_active', 'orders_count']
    list_filter = ['service_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_active']

    def orders_count(self, obj):
        return obj.order_set.count()
    orders_count.short_description = "Количество заказов"

@admin.register(ServiceType, site=admin_site)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'services_count']
    search_fields = ['name']

    def services_count(self, obj):
        return obj.service_set.count()
    services_count.short_description = "Количество услуг"

@admin.register(Employee, site=admin_site)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'phone', 'email', 'hire_date', 'age_display', 'salary']
    list_filter = ['position', 'hire_date', 'specializations']
    search_fields = ['user__first_name', 'user__last_name', 'phone', 'email']
    filter_horizontal = ['specializations']
    readonly_fields = ['age_display']

    def age_display(self, obj):
        return f"{obj.age} лет"
    age_display.short_description = "Возраст"

@admin.register(EmployeeSpecialization, site=admin_site)
class EmployeeSpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'employees_count']
    search_fields = ['name']

    def employees_count(self, obj):
        return obj.employee_set.count()
    employees_count.short_description = "Количество сотрудников"


# === КОНТЕНТ И ОТЗЫВЫ ===

# === FAQ и ВАКАНСИИ ===

@admin.register(FAQ, site=admin_site)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['is_active']

@admin.register(JobVacancy, site=admin_site)
class JobVacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'salary_min', 'salary_max', 'employment_type', 'experience', 'is_active', 'date_posted']
    list_filter = ['employment_type', 'experience', 'is_active', 'date_posted']
    search_fields = ['title', 'description', 'requirements']
    list_editable = ['is_active']
    date_hierarchy = 'date_posted'

# === КОРЗИНА И ЗАЯВКИ ===

@admin.register(Cart, site=admin_site)
class CartAdmin(admin.ModelAdmin):
    list_display = ['client', 'items_count', 'total_price', 'created_at']
    search_fields = ['client__user__first_name', 'client__user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'items_count', 'total_price']

@admin.register(CartItem, site=admin_site)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'service', 'quantity', 'total_price']
    search_fields = ['cart__client__user__first_name', 'service__name']

@admin.register(ServiceRequest, site=admin_site)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['client', 'status', 'total_price', 'assigned_employee', 'created_at']
    list_filter = ['status', 'assigned_employee', 'created_at']
    search_fields = ['client__user__first_name', 'client__user__last_name']
    list_editable = ['status', 'assigned_employee']
    date_hierarchy = 'created_at'

@admin.register(ServiceRequestItem, site=admin_site)
class ServiceRequestItemAdmin(admin.ModelAdmin):
    list_display = ['request', 'service', 'quantity', 'price', 'total_price']
    search_fields = ['request__client__user__first_name', 'service__name']


# Регистрация вспомогательных моделей (скрытых от основного интерфейса)
admin_site.register(RepairSparePart)

# Убираем дублирующую модель Part из старой админки, используем только SparePart
