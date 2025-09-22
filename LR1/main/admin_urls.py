from django.urls import path
from . import admin_views

app_name = 'admin_custom'

urlpatterns = [
    # Главная панель
    path('', admin_views.admin_dashboard, name='dashboard'),
    
    # Клиенты
    path('clients/', admin_views.admin_clients_list, name='clients_list'),
    path('clients/add/', admin_views.admin_client_add, name='client_add'),
    path('clients/<int:client_id>/edit/', admin_views.admin_client_edit, name='client_edit'),
    
    # Устройства
    path('devices/', admin_views.admin_devices_list, name='devices_list'),
    path('devices/add/', admin_views.admin_device_add, name='device_add'),
    path('devices/<int:device_id>/edit/', admin_views.admin_device_edit, name='device_edit'),
    
    # Запчасти
    path('spareparts/', admin_views.admin_spareparts_list, name='spareparts_list'),
    path('spareparts/add/', admin_views.admin_sparepart_add, name='sparepart_add'),
    path('spareparts/<int:sparepart_id>/edit/', admin_views.admin_sparepart_edit, name='sparepart_edit'),
    
    # Ремонты
    path('repairs/', admin_views.admin_repairs_list, name='repairs_list'),
    path('repairs/add/', admin_views.admin_repair_add, name='repair_add'),
    path('repairs/<int:repair_id>/edit/', admin_views.admin_repair_edit, name='repair_edit'),
    
    # Отчеты
    path('reports/', admin_views.reports_view, name='reports'),
    
    # API
    path('api/client/<int:client_id>/devices/', admin_views.api_client_devices, name='api_client_devices'),
    path('api/calculate-parts-cost/', admin_views.api_calculate_parts_cost, name='api_calculate_parts_cost'),
    
    # Старые URL для совместимости
    path('repairs-old/', admin_views.repair_list, name='repair_list_old'),
    path('repairs-old/<int:repair_id>/', admin_views.repair_detail, name='repair_detail_old'),
    path('spare-parts-old/', admin_views.spare_parts_list, name='spare_parts_list_old'),
    path('clients-old/<int:client_id>/', admin_views.client_detail, name='client_detail_old'),
    path('statistics/', admin_views.statistics_view, name='admin_statistics'),
]
