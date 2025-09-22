"""
Кастомные админ-панели для управления сервисным центром
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F, Avg, Min, Max
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth, ExtractYear
from datetime import datetime, timedelta
import json
import calendar

from .models import (
    Client, Device, DeviceType, SparePart, Repair, RepairSparePart,
    Service, Employee, Order, Contract, ServiceType
)
from .forms import ServiceForm, DeviceForm, OrderForm


@staff_member_required
def admin_dashboard(request):
    """Главная страница админ-панели"""
    # Статистика
    total_repairs = Repair.objects.count()
    active_repairs = Repair.objects.filter(status__in=['received', 'in_progress', 'waiting_parts']).count()
    completed_repairs = Repair.objects.filter(status='completed').count()
    total_clients = Client.objects.count()
    total_revenue = Repair.objects.filter(status='completed').aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    
    # Последние ремонты
    recent_repairs = Repair.objects.select_related('client__user', 'device').order_by('-created_at')[:10]
    
    # Популярные запчасти
    popular_parts = SparePart.objects.annotate(
        usage_count=Count('repairsparepart')
    ).order_by('-usage_count')[:5]
    
    # Статистика по статусам
    status_stats = Repair.objects.values('status').annotate(count=Count('id'))
    
    context = {
        'total_repairs': total_repairs,
        'active_repairs': active_repairs,
        'completed_repairs': completed_repairs,
        'total_clients': total_clients,
        'total_revenue': total_revenue,
        'recent_repairs': recent_repairs,
        'popular_parts': popular_parts,
        'status_stats': status_stats,
    }
    
    return render(request, 'admin_custom/dashboard.html', context)


@staff_member_required
def repair_list(request):
    """Список ремонтов с фильтрацией"""
    repairs = Repair.objects.select_related('client__user', 'device', 'device__device_type').order_by('-created_at')
    
    status_filter = request.GET.get('status')
    if status_filter:
        repairs = repairs.filter(status=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        repairs = repairs.filter(
            Q(client__user__first_name__icontains=search_query) |
            Q(client__user__last_name__icontains=search_query) |
            Q(device__name__icontains=search_query) |
            Q(device__model__icontains=search_query)
        )
    
    # Пагинация
    paginator = Paginator(repairs, 20)
    page_number = request.GET.get('page')
    repairs_page = paginator.get_page(page_number)
    
    context = {
        'repairs': repairs_page,
        'status_choices': Repair.STATUS_CHOICES,
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_custom/repair_list.html', context)


@staff_member_required
def repair_detail(request, repair_id):
    """Детали ремонта с возможностью редактирования"""
    repair = get_object_or_404(Repair, id=repair_id)
    spare_parts_used = RepairSparePart.objects.filter(repair=repair).select_related('spare_part')
    
    if request.method == 'POST':
        # Обновление статуса
        new_status = request.POST.get('status')
        if new_status in dict(Repair.STATUS_CHOICES):
            repair.status = new_status
            if new_status == 'completed' and not repair.completed_at:
                repair.completed_at = timezone.now()
            repair.save()
            messages.success(request, 'Статус ремонта обновлен')
            return redirect('admin_custom:repair_detail', repair_id=repair.id)
    
    context = {
        'repair': repair,
        'spare_parts_used': spare_parts_used,
        'status_choices': Repair.STATUS_CHOICES,
    }
    
    return render(request, 'admin_custom/repair_detail.html', context)


@staff_member_required
def add_repair(request):
    """Добавление нового ремонта"""
    if request.method == 'POST':
        client_id = request.POST.get('client')
        device_id = request.POST.get('device')
        description = request.POST.get('description')
        labor_cost = request.POST.get('labor_cost')
        
        try:
            client = Client.objects.get(id=client_id)
            device = Device.objects.get(id=device_id)
            
            repair = Repair.objects.create(
                client=client,
                device=device,
                description=description,
                labor_cost=Decimal(labor_cost)
            )
            
            messages.success(request, f'Ремонт #{repair.id} успешно создан')
            return redirect('admin_custom:repair_detail', repair_id=repair.id)
            
        except (Client.DoesNotExist, Device.DoesNotExist, ValueError) as e:
            messages.error(request, f'Ошибка при создании ремонта: {e}')
    
    clients = Client.objects.select_related('user').all()
    devices = Device.objects.select_related('device_type').all()
    
    context = {
        'clients': clients,
        'devices': devices,
    }
    
    return render(request, 'admin_custom/add_repair.html', context)


@staff_member_required
def add_spare_part_to_repair(request, repair_id):
    """Добавление запчасти к ремонту"""
    repair = get_object_or_404(Repair, id=repair_id)
    
    if request.method == 'POST':
        spare_part_id = request.POST.get('spare_part')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            spare_part = SparePart.objects.get(id=spare_part_id)
            
            # Проверяем наличие на складе
            if spare_part.quantity_in_stock < quantity:
                messages.error(request, f'Недостаточно запчастей на складе. Доступно: {spare_part.quantity_in_stock}')
                return redirect('admin_custom:repair_detail', repair_id=repair.id)
            
            # Создаем или обновляем запись
            repair_spare_part, created = RepairSparePart.objects.get_or_create(
                repair=repair,
                spare_part=spare_part,
                defaults={'quantity': quantity}
            )
            
            if not created:
                repair_spare_part.quantity += quantity
                repair_spare_part.save()
            
            # Уменьшаем количество на складе
            spare_part.quantity_in_stock -= quantity
            spare_part.save()
            
            # Пересчитываем стоимость ремонта
            repair.calculate_total_cost()
            repair.save()
            
            messages.success(request, f'Запчасть "{spare_part.name}" добавлена к ремонту')
            
        except SparePart.DoesNotExist:
            messages.error(request, 'Запчасть не найдена')
    
    return redirect('admin_custom:repair_detail', repair_id=repair.id)


@staff_member_required
def spare_parts_list(request):
    """Список запчастей"""
    spare_parts = SparePart.objects.all().order_by('category', 'name')
    
    # Фильтрация по категории
    category_filter = request.GET.get('category')
    if category_filter:
        spare_parts = spare_parts.filter(category=category_filter)
    
    # Поиск
    search_query = request.GET.get('search')
    if search_query:
        spare_parts = spare_parts.filter(name__icontains=search_query)
    
    # Фильтр по наличию
    stock_filter = request.GET.get('stock')
    if stock_filter == 'in_stock':
        spare_parts = spare_parts.filter(quantity_in_stock__gt=0)
    elif stock_filter == 'out_of_stock':
        spare_parts = spare_parts.filter(quantity_in_stock=0)
    elif stock_filter == 'low_stock':
        spare_parts = spare_parts.filter(quantity_in_stock__lt=5, quantity_in_stock__gt=0)
    
    # Получаем уникальные категории
    categories = SparePart.objects.values_list('category', flat=True).distinct().order_by('category')
    
    # Пагинация
    paginator = Paginator(spare_parts, 20)
    page_number = request.GET.get('page')
    spare_parts_page = paginator.get_page(page_number)
    
    context = {
        'spare_parts': spare_parts_page,
        'categories': categories,
        'current_category': category_filter,
        'search_query': search_query,
        'current_stock': stock_filter,
    }
    
    return render(request, 'admin_custom/spare_parts_list.html', context)


@staff_member_required
def add_spare_part(request):
    """Добавление новой запчасти"""
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity_in_stock', 0)
        
        try:
            spare_part = SparePart.objects.create(
                name=name,
                category=category,
                price=Decimal(price),
                quantity_in_stock=int(quantity)
            )
            
            messages.success(request, f'Запчасть "{spare_part.name}" успешно добавлена')
            return redirect('admin_custom:spare_parts_list')
            
        except ValueError as e:
            messages.error(request, f'Ошибка при создании запчасти: {e}')
    
    # Получаем существующие категории
    categories = SparePart.objects.values_list('category', flat=True).distinct().order_by('category')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'admin_custom/add_spare_part.html', context)


@staff_member_required
def clients_list(request):
    """Список клиентов"""
    clients = Client.objects.select_related('user').order_by('user__last_name', 'user__first_name')
    
    # Поиск
    search_query = request.GET.get('search')
    if search_query:
        clients = clients.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Добавляем статистику по каждому клиенту
    for client in clients:
        client.repairs_count = client.repairs.count()
        client.total_spent = client.repairs.filter(status='completed').aggregate(
            Sum('total_cost'))['total_cost__sum'] or 0
    
    # Пагинация
    paginator = Paginator(clients, 20)
    page_number = request.GET.get('page')
    clients_page = paginator.get_page(page_number)
    
    context = {
        'clients': clients_page,
        'search_query': search_query,
    }
    
    return render(request, 'admin_custom/clients_list.html', context)


@staff_member_required
def client_detail(request, client_id):
    """Детали клиента и его ремонты"""
    client = get_object_or_404(Client, id=client_id)
    repairs = client.repairs.order_by('-created_at')
    
    # Статистика клиента
    total_repairs = repairs.count()
    completed_repairs = repairs.filter(status='completed').count()
    total_spent = repairs.filter(status='completed').aggregate(
        Sum('total_cost'))['total_cost__sum'] or 0
    
    context = {
        'client': client,
        'repairs': repairs,
        'total_repairs': total_repairs,
        'completed_repairs': completed_repairs,
        'total_spent': total_spent,
    }
    
    return render(request, 'admin_custom/client_detail.html', context)


@staff_member_required
def statistics_view(request):
    """Статистика и отчеты с графиками"""
    # Общая статистика
    total_repairs = Repair.objects.count()
    total_revenue = Repair.objects.filter(status='completed').aggregate(
        Sum('total_cost'))['total_cost__sum'] or 0
    
    # Средняя стоимость ремонта
    completed_repairs_count = Repair.objects.filter(status='completed').count()
    avg_repair_cost = 0
    if completed_repairs_count > 0:
        avg_repair_cost = total_revenue / completed_repairs_count
    
    # Общее количество клиентов
    total_clients = Client.objects.count()
    
    # Статистика по статусам для круговой диаграммы
    status_stats = Repair.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    status_labels = [item['status'] for item in status_stats]
    status_counts = [item['count'] for item in status_stats]
    
    # Статистика по месяцам для линейной диаграммы
    current_year = timezone.now().year
    monthly_repairs = []
    monthly_revenue = []
    months_labels = []
    
    for month in range(1, 13):
        month_name = calendar.month_name[month]
        months_labels.append(month_name)
        
        month_repairs = Repair.objects.filter(
            created_at__year=current_year,
            created_at__month=month
        ).count()
        monthly_repairs.append(month_repairs)
        
        month_revenue = Repair.objects.filter(
            created_at__year=current_year,
            created_at__month=month,
            status='completed'
        ).aggregate(Sum('total_cost'))['total_cost__sum'] or 0
        monthly_revenue.append(float(month_revenue))
    
    # Топ-5 клиентов по расходам для столбчатой диаграммы
    top_clients = Client.objects.annotate(
        total_spent=Sum('repairs__total_cost', filter=Q(repairs__status='completed')),
        repairs_count=Count('repairs', filter=Q(repairs__status='completed'))
    ).filter(total_spent__gt=0).order_by('-total_spent')[:5]
    
    client_names = [f"{client.user.first_name} {client.user.last_name}" for client in top_clients]
    client_spent = [float(client.total_spent or 0) for client in top_clients]
    
    # Популярные запчасти для столбчатой диаграммы
    popular_parts = SparePart.objects.annotate(
        usage_count=Count('repairsparepart'),
        total_sold=Sum('repairsparepart__quantity')
    ).filter(usage_count__gt=0).order_by('-usage_count')[:5]
    
    part_names = [part.name for part in popular_parts]
    part_counts = [part.usage_count for part in popular_parts]
    
    # Динамика доходов по годам
    yearly_revenue = Repair.objects.filter(
        status='completed'
    ).annotate(
        year=ExtractYear('created_at')
    ).values('year').annotate(
        total=Sum('total_cost')
    ).order_by('year')
    
    years = [item['year'] for item in yearly_revenue]
    yearly_totals = [float(item['total']) for item in yearly_revenue]
    
    context = {
        'total_repairs': total_repairs,
        'total_revenue': total_revenue,
        'avg_repair_cost': avg_repair_cost,
        'total_clients': total_clients,
        'status_labels': status_labels,
        'status_counts': status_counts,
        'months_labels': months_labels,
        'monthly_repairs': monthly_repairs,
        'monthly_revenue': monthly_revenue,
        'client_names': client_names,
        'client_spent': client_spent,
        'part_names': part_names,
        'part_counts': part_counts,
        'years': years,
        'yearly_totals': yearly_totals,
    }
    
    return render(request, 'admin_custom/statistics.html', context)


# ================ НОВАЯ HTML АДМИНКА ================

@staff_member_required
def admin_clients_list(request):
    """Список клиентов"""
    search = request.GET.get('search', '')
    clients = Client.objects.all()
    
    if search:
        clients = clients.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    paginator = Paginator(clients, 20)
    page = request.GET.get('page')
    clients = paginator.get_page(page)
    
    return render(request, 'admin_custom/clients_list.html', {
        'clients': clients,
        'search': search
    })

@staff_member_required
def admin_client_add(request):
    """Добавление клиента"""
    if request.method == 'POST':
        # Создаем пользователя
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password='temp123'  # Временный пароль
            )
            
            client = Client.objects.create(
                user=user,
                phone=phone,
                address=address
            )
            
            messages.success(request, f'Клиент {client.user.get_full_name()} успешно добавлен')
            return redirect('admin_clients_list')
    
    return render(request, 'admin_custom/client_form.html')

@staff_member_required
def admin_client_edit(request, client_id):
    """Редактирование клиента"""
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == 'POST':
        client.user.first_name = request.POST.get('first_name')
        client.user.last_name = request.POST.get('last_name')
        client.user.email = request.POST.get('email')
        client.phone = request.POST.get('phone')
        client.address = request.POST.get('address')
        
        client.user.save()
        client.save()
        
        messages.success(request, 'Клиент успешно обновлен')
        return redirect('admin_clients_list')
    
    return render(request, 'admin_custom/client_form.html', {'client': client})

@staff_member_required
def admin_devices_list(request):
    """Список устройств"""
    search = request.GET.get('search', '')
    devices = Device.objects.select_related('client__user', 'device_type')
    
    if search:
        devices = devices.filter(
            Q(name__icontains=search) |
            Q(serial_number__icontains=search) |
            Q(client__user__first_name__icontains=search) |
            Q(client__user__last_name__icontains=search)
        )
    
    paginator = Paginator(devices, 20)
    page = request.GET.get('page')
    devices = paginator.get_page(page)
    
    return render(request, 'admin_custom/devices_list.html', {
        'devices': devices,
        'search': search
    })

@staff_member_required
def admin_device_add(request):
    """Добавление устройства"""
    if request.method == 'POST':
        client_id = request.POST.get('client')
        device_type_id = request.POST.get('device_type')
        name = request.POST.get('name')
        serial_number = request.POST.get('serial_number')
        description = request.POST.get('description', '')
        
        client = get_object_or_404(Client, id=client_id)
        device_type = get_object_or_404(DeviceType, id=device_type_id)
        
        device = Device.objects.create(
            client=client,
            device_type=device_type,
            name=name,
            serial_number=serial_number,
            description=description
        )
        
        messages.success(request, f'Устройство {device.name} успешно добавлено')
        return redirect('admin_devices_list')
    
    clients = Client.objects.all()
    device_types = DeviceType.objects.all()
    
    return render(request, 'admin_custom/device_form.html', {
        'clients': clients,
        'device_types': device_types
    })

@staff_member_required
def admin_device_edit(request, device_id):
    """Редактирование устройства"""
    device = get_object_or_404(Device, id=device_id)
    
    if request.method == 'POST':
        client_id = request.POST.get('client')
        device_type_id = request.POST.get('device_type')
        
        device.client = get_object_or_404(Client, id=client_id)
        device.device_type = get_object_or_404(DeviceType, id=device_type_id)
        device.name = request.POST.get('name')
        device.serial_number = request.POST.get('serial_number')
        device.description = request.POST.get('description', '')
        device.save()
        
        messages.success(request, 'Устройство успешно обновлено')
        return redirect('admin_devices_list')
    
    clients = Client.objects.all()
    device_types = DeviceType.objects.all()
    
    return render(request, 'admin_custom/device_form.html', {
        'device': device,
        'clients': clients,
        'device_types': device_types
    })

@staff_member_required
def admin_spareparts_list(request):
    """Список запчастей"""
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    
    spareparts = SparePart.objects.all()
    
    if search:
        spareparts = spareparts.filter(
            Q(name__icontains=search) |
            Q(part_number__icontains=search) |
            Q(category__icontains=search)
        )
    
    if category:
        spareparts = spareparts.filter(category=category)
    
    # Получаем уникальные категории для фильтра
    categories = SparePart.objects.values_list('category', flat=True).distinct()
    
    paginator = Paginator(spareparts, 20)
    page = request.GET.get('page')
    spareparts = paginator.get_page(page)
    
    return render(request, 'admin_custom/spareparts_list.html', {
        'spareparts': spareparts,
        'search': search,
        'category': category,
        'categories': categories
    })

@staff_member_required
def admin_sparepart_add(request):
    """Добавление запчасти"""
    if request.method == 'POST':
        name = request.POST.get('name')
        part_number = request.POST.get('part_number')
        category = request.POST.get('category')
        price = request.POST.get('price')
        quantity_in_stock = request.POST.get('quantity_in_stock')
        description = request.POST.get('description', '')
        
        sparepart = SparePart.objects.create(
            name=name,
            part_number=part_number,
            category=category,
            price=Decimal(price),
            quantity_in_stock=int(quantity_in_stock),
            description=description
        )
        
        messages.success(request, f'Запчасть {sparepart.name} успешно добавлена')
        return redirect('admin_spareparts_list')
    
    # Получаем существующие категории для выпадающего списка
    categories = SparePart.objects.values_list('category', flat=True).distinct()
    
    return render(request, 'admin_custom/sparepart_form.html', {
        'categories': categories
    })

@staff_member_required
def admin_sparepart_edit(request, sparepart_id):
    """Редактирование запчасти"""
    sparepart = get_object_or_404(SparePart, id=sparepart_id)
    
    if request.method == 'POST':
        sparepart.name = request.POST.get('name')
        sparepart.part_number = request.POST.get('part_number')
        sparepart.category = request.POST.get('category')
        sparepart.price = Decimal(request.POST.get('price'))
        sparepart.quantity_in_stock = int(request.POST.get('quantity_in_stock'))
        sparepart.description = request.POST.get('description', '')
        sparepart.save()
        
        messages.success(request, 'Запчасть успешно обновлена')
        return redirect('admin_spareparts_list')
    
    categories = SparePart.objects.values_list('category', flat=True).distinct()
    
    return render(request, 'admin_custom/sparepart_form.html', {
        'sparepart': sparepart,
        'categories': categories
    })

@staff_member_required
def admin_repairs_list(request):
    """Список ремонтов"""
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    repairs = Repair.objects.select_related('client__user', 'device', 'assigned_employee__user')
    
    if search:
        repairs = repairs.filter(
            Q(client__user__first_name__icontains=search) |
            Q(client__user__last_name__icontains=search) |
            Q(device__name__icontains=search) |
            Q(problem_description__icontains=search)
        )
    
    if status:
        repairs = repairs.filter(status=status)
    
    # Статусы для фильтра
    status_choices = [
        ('received', 'Принят'),
        ('diagnosed', 'Диагностирован'),
        ('in_progress', 'В работе'),
        ('waiting_parts', 'Ожидание запчастей'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен')
    ]
    
    paginator = Paginator(repairs, 20)
    page = request.GET.get('page')
    repairs = paginator.get_page(page)
    
    return render(request, 'admin_custom/repairs_list.html', {
        'repairs': repairs,
        'search': search,
        'status': status,
        'status_choices': status_choices
    })

@staff_member_required
def admin_repair_add(request):
    """Добавление ремонта"""
    if request.method == 'POST':
        client_id = request.POST.get('client')
        device_id = request.POST.get('device')
        problem_description = request.POST.get('problem_description')
        assigned_employee_id = request.POST.get('assigned_employee')
        
        client = get_object_or_404(Client, id=client_id)
        device = get_object_or_404(Device, id=device_id)
        
        repair = Repair.objects.create(
            client=client,
            device=device,
            problem_description=problem_description,
            status='received'
        )
        
        if assigned_employee_id:
            employee = get_object_or_404(Employee, id=assigned_employee_id)
            repair.assigned_employee = employee
            repair.save()
        
        messages.success(request, f'Ремонт #{repair.id} успешно создан')
        return redirect('admin_repairs_list')
    
    clients = Client.objects.all()
    employees = Employee.objects.all()
    
    return render(request, 'admin_custom/repair_form.html', {
        'clients': clients,
        'employees': employees
    })

@staff_member_required
def admin_repair_edit(request, repair_id):
    """Редактирование ремонта с автоматическим расчетом стоимости"""
    repair = get_object_or_404(Repair, id=repair_id)
    
    if request.method == 'POST':
        # Основные поля
        repair.problem_description = request.POST.get('problem_description')
        repair.diagnosis = request.POST.get('diagnosis', '')
        repair.status = request.POST.get('status')
        repair.work_cost = Decimal(request.POST.get('work_cost', '0'))
        
        # Назначение сотрудника
        assigned_employee_id = request.POST.get('assigned_employee')
        if assigned_employee_id:
            repair.assigned_employee = get_object_or_404(Employee, id=assigned_employee_id)
        
        # Обработка запчастей
        sparepart_ids = request.POST.getlist('sparepart_id[]')
        quantities = request.POST.getlist('quantity[]')
        
        # Удаляем старые связи с запчастями
        RepairSparePart.objects.filter(repair=repair).delete()
        
        # Добавляем новые запчасти и рассчитываем стоимость
        parts_total = Decimal('0')
        for i, sparepart_id in enumerate(sparepart_ids):
            if sparepart_id and i < len(quantities):
                sparepart = get_object_or_404(SparePart, id=sparepart_id)
                quantity = int(quantities[i])
                
                RepairSparePart.objects.create(
                    repair=repair,
                    spare_part=sparepart,
                    quantity=quantity
                )
                
                parts_total += sparepart.price * quantity
        
        # Автоматический расчет общей стоимости
        repair.total_cost = repair.work_cost + parts_total
        repair.save()
        
        messages.success(request, f'Ремонт #{repair.id} успешно обновлен. Общая стоимость: {repair.total_cost} руб.')
        return redirect('admin_repairs_list')
    
    clients = Client.objects.all()
    employees = Employee.objects.all()
    spareparts = SparePart.objects.all()
    repair_spareparts = RepairSparePart.objects.filter(repair=repair)
    
    return render(request, 'admin_custom/repair_form.html', {
        'repair': repair,
        'clients': clients,
        'employees': employees,
        'spareparts': spareparts,
        'repair_spareparts': repair_spareparts
    })

@staff_member_required
def admin_reports(request):
    """Отчеты и аналитика"""
    # Параметры фильтрации
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', '')
    client_id = request.GET.get('client', '')
    
    # Базовый фильтр
    repairs = Repair.objects.filter(status='completed', created_at__year=year)
    
    if month:
        repairs = repairs.filter(created_at__month=month)
    
    if client_id:
        repairs = repairs.filter(client_id=client_id)
    
    # Статистика по клиентам
    client_stats = repairs.values(
        'client__user__first_name', 
        'client__user__last_name',
        'client_id'
    ).annotate(
        total_repairs=Count('id'),
        total_amount=Sum('total_cost')
    ).order_by('-total_amount')
    
    # Статистика по месяцам
    monthly_stats = Repair.objects.filter(
        status='completed', 
        created_at__year=year
    ).extra(
        select={'month': "strftime('%%m', created_at)"}
    ).values('month').annotate(
        total_repairs=Count('id'),
        total_amount=Sum('total_cost')
    ).order_by('month')
    
    # Популярные запчасти
    popular_parts = SparePart.objects.annotate(
        usage_count=Count('repairsparepart__repair', 
                         filter=Q(repairsparepart__repair__status='completed')),
        total_revenue=Sum(F('repairsparepart__quantity') * F('price'),
                         filter=Q(repairsparepart__repair__status='completed'))
    ).filter(usage_count__gt=0).order_by('-usage_count')[:10]
    
    # Общая статистика
    total_revenue = repairs.aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    total_repairs_count = repairs.count()
    avg_repair_cost = total_revenue / total_repairs_count if total_repairs_count > 0 else 0
    
    context = {
        'year': int(year),
        'month': month,
        'client_id': client_id,
        'client_stats': client_stats,
        'monthly_stats': monthly_stats,
        'popular_parts': popular_parts,
        'total_revenue': total_revenue,
        'total_repairs_count': total_repairs_count,
        'avg_repair_cost': avg_repair_cost,
        'clients': Client.objects.all(),
        'years': range(2020, timezone.now().year + 2),
        'months': [
            (1, 'Январь'), (2, 'Февраль'), (3, 'Март'), (4, 'Апрель'),
            (5, 'Май'), (6, 'Июнь'), (7, 'Июль'), (8, 'Август'),
            (9, 'Сентябрь'), (10, 'Октябрь'), (11, 'Ноябрь'), (12, 'Декабрь')
        ]
    }
    
    return render(request, 'admin_custom/reports.html', context)

# API для автозагрузки устройств клиента
@staff_member_required
def api_client_devices(request, client_id):
    """API для получения устройств клиента"""
    devices = Device.objects.filter(client_id=client_id).values('id', 'name', 'serial_number')
    return JsonResponse({'devices': list(devices)})

# API для расчета стоимости запчастей
@staff_member_required
def api_calculate_parts_cost(request):
    """API для расчета стоимости выбранных запчастей"""
    if request.method == 'POST':
        data = json.loads(request.body)
        parts = data.get('parts', [])
        
        total_cost = Decimal('0')
        for part in parts:
            sparepart = get_object_or_404(SparePart, id=part['id'])
            quantity = int(part['quantity'])
            total_cost += sparepart.price * quantity
        
        return JsonResponse({'total_cost': float(total_cost)})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@staff_member_required
def reports_view(request):
    """Страница отчетов с аналитикой"""
    # Получение параметров фильтров
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    selected_client = request.GET.get('client')
    
    # Базовый queryset для ремонтов
    repairs_qs = Repair.objects.filter(status='completed')
    
    # Применение фильтров
    if selected_year:
        repairs_qs = repairs_qs.filter(created_at__year=selected_year)
    if selected_month:
        repairs_qs = repairs_qs.filter(created_at__month=selected_month)
    if selected_client:
        repairs_qs = repairs_qs.filter(client_id=selected_client)
    
    # Общая статистика
    total_revenue = repairs_qs.aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    total_repairs = repairs_qs.count()
    avg_repair_cost = repairs_qs.aggregate(Avg('total_cost'))['total_cost__avg'] or 0
    active_clients = repairs_qs.values('client').distinct().count()
    
    # Отчет по клиентам
    client_reports = repairs_qs.values(
        'client__user__first_name', 'client__user__last_name'
    ).annotate(
        client_name=F('client__user__first_name') + ' ' + F('client__user__last_name'),
        repair_count=Count('id'),
        total_amount=Sum('total_cost'),
        avg_amount=Avg('total_cost'),
        last_repair_date=F('created_at')
    ).order_by('-total_amount')
    
    # Отчет по месяцам
    monthly_reports = repairs_qs.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        repair_count=Count('id'),
        total_amount=Sum('total_cost'),
        avg_amount=Avg('total_cost')
    ).order_by('month')
    
    # Топ запчастей
    top_parts = RepairSparePart.objects.filter(
        repair__in=repairs_qs
    ).values(
        'spare_part__name'
    ).annotate(
        name=F('spare_part__name'),
        usage_count=Count('repair'),
        total_quantity=Sum('quantity'),
        total_cost=Sum(F('quantity') * F('spare_part__price'))
    ).order_by('-usage_count')[:10]
    
    # Данные для графика (последние 12 месяцев)
    last_year = timezone.now() - timedelta(days=365)
    monthly_chart_data = Repair.objects.filter(
        status='completed',
        created_at__gte=last_year
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('total_cost')
    ).order_by('month')
    
    chart_labels = []
    chart_data = []
    for item in monthly_chart_data:
        chart_labels.append(item['month'].strftime('%Y-%m'))
        chart_data.append(float(item['total'] or 0))
    
    # Доступные годы для фильтра
    years = Repair.objects.dates('created_at', 'year', order='DESC').values_list('created_at__year', flat=True)
    
    # Список клиентов для фильтра
    clients = Client.objects.select_related('user').all()
    
    context = {
        'total_revenue': total_revenue,
        'total_repairs': total_repairs,
        'avg_repair_cost': avg_repair_cost,
        'active_clients': active_clients,
        'client_reports': client_reports,
        'monthly_reports': monthly_reports,
        'top_parts': top_parts,
        'monthly_chart_data': json.dumps({
            'labels': chart_labels,
            'data': chart_data
        }),
        'years': years,
        'clients': clients,
        'selected_year': int(selected_year) if selected_year else None,
        'selected_month': selected_month,
        'selected_client': int(selected_client) if selected_client else None,
    }
    
    return render(request, 'admin_custom/reports.html', context)
