from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q, Sum, Avg, Count, Max, Min
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
import logging
import calendar
from datetime import datetime, date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import random

from .models import (
    Client, Employee, Service, ServiceType, Repair, SparePart, 
    News, Review, CompanyInfo, Vacancy, Order, Contract, PromoCode,
    Term, JobVacancy, Cart, CartItem, ServiceRequest, ServiceRequestItem,
    Schedule
)
from .forms import ReviewForm, ClientProfileForm

logger = logging.getLogger(__name__)

# Список случайных изображений для новостей
RANDOM_NEWS_IMAGES = [
    'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1556761175-4b46a572b786?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1515343480029-43cdfe6b6aae?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1563770660941-10a9f689d08e?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1597740985671-2a8a3b80502e?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=800&h=600&fit=crop',
]

# === ОСНОВНЫЕ СТРАНИЦЫ ===

def index(request):
    """Главная страница"""
    try:
        latest_news = News.objects.filter(is_published=True).latest('created_at')
        # Добавляем случайное изображение если его нет
        if latest_news and not latest_news.image_url and not latest_news.image:
            latest_news.random_image_url = random.choice(RANDOM_NEWS_IMAGES)
    except News.DoesNotExist:
        latest_news = None
    
    return render(request, 'main/index.html', {
        'latest_news': latest_news
    })

def about_company(request):
    """О компании"""
    company_info = CompanyInfo.objects.first()
    return render(request, 'main/about.html', {'company_info': company_info})

def terms_list(request):
    """Словарь терминов (FAQ)"""
    terms = Term.objects.all()
    return render(request, 'main/terms_list.html', {'terms': terms})

def faq_list(request):
    """FAQ страница"""
    terms = Term.objects.all()
    return render(request, 'main/faq.html', {'terms': terms})

def contacts(request):
    """Контакты - сотрудники"""
    employees = Employee.objects.all()
    return render(request, 'main/contacts.html', {'employees': employees})

def company_policy(request):
    """Политика компании"""
    return render(request, 'main/company_policy.html')

def vacancies_list(request):
    """Список вакансий"""
    vacancies = JobVacancy.objects.filter(is_active=True).order_by('-date_posted')
    return render(request, 'main/vacancies.html', {'vacancies': vacancies})

def reviews_list(request):
    """Список отзывов"""
    reviews = Review.objects.filter(is_moderated=True)
    return render(request, 'main/reviews.html', {'reviews': reviews})

def promocodes_list(request):
    """Список промокодов"""
    now = timezone.now()
    active_codes = PromoCode.objects.filter(is_active=True, valid_until__gte=now)
    return render(request, 'main/promocodes.html', {'active_codes': active_codes})

@login_required
def add_review(request):
    """Добавление отзыва"""
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        messages.error(request, 'Для оставления отзыва необходимо завершить регистрацию как клиент.')
        return redirect('main:create_client_profile')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = client
            review.save()
            messages.success(request, 'Отзыв добавлен и отправлен на модерацию')
            return redirect('main:reviews_list')
    else:
        form = ReviewForm()
    
    return render(request, 'main/add_review.html', {'form': form})

@login_required
def create_client_profile(request):
    """Создание профиля клиента для зарегистрированного пользователя"""
    try:
        client = Client.objects.get(user=request.user)
        messages.info(request, 'У вас уже есть профиль клиента')
        return redirect('main:index')
    except Client.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = ClientProfileForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            messages.success(request, 'Профиль клиента успешно создан!')
            return redirect('main:client_dashboard')
    else:
        form = ClientProfileForm()
    
    return render(request, 'main/create_client_profile.html', {'form': form})


class NewsListView(ListView):
    """Список новостей"""
    model = News
    template_name = 'main/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10
    
    def get_queryset(self):
        return News.objects.filter(is_published=True).order_by('-created_at')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        for news in context['news_list']:
            if not news.image_url and not news.image:
                news.random_image_url = random.choice(RANDOM_NEWS_IMAGES)
                
        return context

class NewsDetailView(DetailView):
    """Детали новости"""
    model = News
    template_name = 'main/news_detail.html'
    context_object_name = 'news'
    
    def get_queryset(self):
        return News.objects.filter(is_published=True)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        news = context['news']
        if not news.image_url and not news.image:
            news.random_image_url = random.choice(RANDOM_NEWS_IMAGES)
                
        return context

@login_required
def create_news_with_images(request):
    """Страница для создания новостей с изображениями из API"""
    return render(request, 'main/create_news_with_images.html')

class ServiceListView(ListView):
    """Список услуг с фильтрацией и сортировкой"""
    model = Service
    template_name = 'main/service_list.html'
    context_object_name = 'services'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Service.objects.select_related('service_type').filter(is_active=True)
        
        # Фильтрация по поиску
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category and category != 'all':
            try:
                queryset = queryset.filter(service_type_id=int(category))
            except (ValueError, TypeError):
                pass
        
        # Фильтрация по минимальной цене
        min_price = self.request.GET.get('min_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except (ValueError, TypeError):
                pass
                
        # Фильтрация по максимальной цене
        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass
        
        # Сортировка
        sort_by = self.request.GET.get('sort', 'name')
        if sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'category':
            queryset = queryset.order_by('service_type__name', 'name')
        else:
            queryset = queryset.order_by('name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_types'] = ServiceType.objects.all()
        context['current_search'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', 'all')
        context['current_min_price'] = self.request.GET.get('min_price', '')
        context['current_max_price'] = self.request.GET.get('max_price', '')
        context['current_sort'] = self.request.GET.get('sort', 'name')
        
        # Добавляем статистику для отображения диапазона цен
        price_range = Service.objects.filter(is_active=True).aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        context['min_price_available'] = price_range['min_price'] or 0
        context['max_price_available'] = price_range['max_price'] or 1000
        
        return context

def terms_list(request):
    """Словарь терминов (FAQ)"""
    terms = Term.objects.all()
    return render(request, 'main/terms_list.html', {'terms': terms})

def contacts(request):
    """Контакты - сотрудники"""
    employees = Employee.objects.all()
    return render(request, 'main/contacts.html', {'employees': employees})


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
def cart_view(request):
    """Просмотр корзины"""
    try:
        client = request.user.client
    except:
        messages.error(request, "Доступ к корзине только для зарегистрированных клиентов")
        return redirect('main:service_list')
    
    cart, created = Cart.objects.get_or_create(client=client)
    
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('service', 'service__service_type'),
        'total_price': cart.total_price,
        'items_count': cart.items_count,
    }
    return render(request, 'main/cart.html', context)


@login_required
@require_POST
def add_to_cart(request, service_id):
    """Добавить услугу в корзину"""
    try:
        client = request.user.client
    except:
        messages.error(request, "Доступ к корзине только для зарегистрированных клиентов")
        return redirect('main:service_list')
    
    service = get_object_or_404(Service, id=service_id, is_active=True)
    cart, created = Cart.objects.get_or_create(client=client)
    
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        service=service,
        defaults={'quantity': quantity}
    )
    
    if not item_created:
        # Если услуга уже в корзине, увеличиваем количество
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f"Количество услуги '{service.name}' увеличено до {cart_item.quantity}")
    else:
        messages.success(request, f"Услуга '{service.name}' добавлена в корзину")
    
    return redirect('main:cart')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Удалить услугу из корзины"""
    try:
        client = request.user.client
    except:
        messages.error(request, "Доступ к корзине только для зарегистрированных клиентов")
        return redirect('main:service_list')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__client=client)
    service_name = cart_item.service.name
    cart_item.delete()
    
    messages.success(request, f"Услуга '{service_name}' удалена из корзины")
    return redirect('main:cart')


@login_required
@require_POST
def update_cart_item(request, item_id):
    """Обновить количество услуги в корзине"""
    try:
        client = request.user.client
    except:
        messages.error(request, "Доступ к корзине только для зарегистрированных клиентов")
        return redirect('main:service_list')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__client=client)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f"Количество услуги '{cart_item.service.name}' обновлено")
    else:
        service_name = cart_item.service.name
        cart_item.delete()
        messages.success(request, f"Услуга '{service_name}' удалена из корзины")
    
    return redirect('main:cart')


@login_required
def submit_service_request(request):
    """Подать заявку на услуги из корзины"""
    try:
        client = request.user.client
    except:
        messages.error(request, "Доступ к корзине только для зарегистрированных клиентов")
        return redirect('main:service_list')
    
    cart = get_object_or_404(Cart, client=client)
    
    if not cart.items.exists():
        messages.error(request, "Корзина пуста. Добавьте услуги для подачи заявки")
        return redirect('main:cart')
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        
        # Создаем заявку
        service_request = ServiceRequest.objects.create(
            client=client,
            notes=notes,
            status='pending'
        )
        
        # Переносим услуги из корзины в заявку
        total_price = 0
        for cart_item in cart.items.all():
            ServiceRequestItem.objects.create(
                request=service_request,
                service=cart_item.service,
                quantity=cart_item.quantity,
                price=cart_item.service.price  # Фиксируем цену на момент заказа
            )
            total_price += cart_item.total_price
        
        # Обновляем общую стоимость заявки
        service_request.total_price = total_price
        service_request.save()
        
        # Очищаем корзину
        cart.items.all().delete()
        
        messages.success(request, f"Заявка #{service_request.id} успешно подана. Ожидайте рассмотрения администратором")
        return redirect('main:service_requests')
    
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('service'),
        'total_price': cart.total_price,
    }
    return render(request, 'main/submit_request.html', context)


@login_required
def service_requests_list(request):
    """Список заявок пользователя"""
    try:
        client = request.user.client
    except:
        messages.error(request, "Доступ к заявкам только для зарегистрированных клиентов")
        return redirect('main:service_list')
    
    requests = ServiceRequest.objects.filter(client=client).prefetch_related(
        'servicerequestitem_set__service'
    ).order_by('-created_at')
    
    context = {
        'requests': requests,
    }
    return render(request, 'main/service_requests.html', context)


@login_required
def service_request_detail(request, request_id):
    """Детали заявки"""
    try:
        client = request.user.client
    except:
        messages.error(request, "Доступ к заявкам только для зарегистрированных клиентов")
        return redirect('main:service_list')
    
    service_request = get_object_or_404(
        ServiceRequest, 
        id=request_id, 
        client=client
    )
    
    context = {
        'service_request': service_request,
        'items': service_request.servicerequestitem_set.select_related('service'),
    }
    return render(request, 'main/service_request_detail.html', context)



from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_service_requests(request):
    """Административный список заявок"""
    status_filter = request.GET.get('status', '')
    
    requests = ServiceRequest.objects.select_related('client__user', 'assigned_employee__user').order_by('-created_at')
    
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    context = {
        'requests': requests,
        'status_choices': ServiceRequest.STATUS_CHOICES,
        'current_status': status_filter,
    }
    return render(request, 'main/admin_service_requests.html', context)


@staff_member_required
def admin_service_request_detail(request, request_id):
    """Административный просмотр заявки"""
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        assigned_employee_id = request.POST.get('assigned_employee')
        
        service_request.status = status
        service_request.admin_notes = admin_notes
        
        if assigned_employee_id:
            service_request.assigned_employee_id = assigned_employee_id
        
        service_request.save()
        
        messages.success(request, f"Заявка #{service_request.id} обновлена")
        return redirect('main:admin_service_requests')
    
    context = {
        'service_request': service_request,
        'items': service_request.servicerequestitem_set.select_related('service'),
        'employees': Employee.objects.all(),
        'status_choices': ServiceRequest.STATUS_CHOICES,
    }
    return render(request, 'main/admin_service_request_detail.html', context)

def privacy_policy(request):
    """Политика конфиденциальности"""
    return render(request, 'main/privacy_policy.html')

def search_view(request):
    """Общий поиск по сайту"""
    query = request.GET.get('q', '')
    results = {}
    
    if query:
        results['services'] = Service.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        )[:5]
        
        results['news'] = News.objects.filter(
            Q(title__icontains=query) | Q(short_description__icontains=query),
            is_published=True
        )[:5]
        
        results['terms'] = Term.objects.filter(
            Q(question__icontains=query) | Q(answer__icontains=query)
        )[:5]
    
    return render(request, 'main/search_results.html', {
        'query': query,
        'results': results
    })

def about(request):
    return HttpResponse("<h1>О компании</h1><p>Мы занимаемся ремонтом техники</p>")

def services(request):
    return HttpResponse("<h1>Наши услуги</h1><p>Ремонт компьютеров, настройка ПО</p>")

@login_required
def create_news_with_images(request):
    """Страница для создания новостей с изображениями из API"""
    return render(request, 'main/create_news_with_images.html')

def master_dashboard(request):
    """Главная страница для мастеров"""
    return render(request, 'main/master_dashboard.html')

@login_required
def statistics(request):
    """Статистика по заявкам и услугам"""
    total_requests = ServiceRequest.objects.count()
    total_services = Service.objects.count()
    total_clients = Client.objects.count()
    total_employees = Employee.objects.count()
    
    # Статистика по заявкам по месяцам
    now = timezone.now()
    requests_by_month = []
    month_labels = []
    
    # Получаем последние 6 месяцев с учетом перехода через год
    for i in range(5, -1, -1):
        # Вычисляем месяц и год
        month = now.month - i
        year = now.year
        
        # Если месяц стал отрицательным или нулевым, корректируем год и месяц
        while month <= 0:
            month += 12
            year -= 1
            
        start_date = timezone.datetime(year, month, 1, 0, 0, 0, 0, tzinfo=timezone.get_current_timezone())
        end_date = start_date + timezone.timedelta(days=calendar.monthrange(year, month)[1])
        
        requests_count = ServiceRequest.objects.filter(created_at__range=(start_date, end_date)).count()
        requests_by_month.append(requests_count)
        month_labels.append(start_date.strftime('%B %Y'))
    
    plt.figure(figsize=(10, 6))
    plt.bar(month_labels, requests_by_month, color='skyblue')
    plt.title('Количество заявок по месяцам')
    plt.xlabel('Месяц')
    plt.ylabel('Количество заявок')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    monthly_chart = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    top_services = Service.objects.annotate(total_requests=Count('servicerequestitem')).order_by('-total_requests')[:5]
    
    plt.figure(figsize=(10, 6))
    service_names = [service.name for service in top_services]
    service_counts = [service.total_requests for service in top_services]
    
    plt.barh(service_names, service_counts, color='lightgreen')
    plt.title('Топ-5 популярных услуг')
    plt.xlabel('Количество заявок')
    plt.ylabel('Услуга')
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    services_chart = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    status_stats = ServiceRequest.objects.values('status').annotate(count=Count('id'))
    
    plt.figure(figsize=(8, 8))
    status_labels = [item['status'] for item in status_stats]
    status_counts = [item['count'] for item in status_stats]
    
    plt.pie(status_counts, labels=status_labels, autopct='%1.1f%%', colors=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow'])
    plt.title('Распределение заявок по статусам')
    plt.axis('equal')
    
    # Сохраняем график в буфер
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    status_chart = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    context = {
        'total_requests': total_requests,
        'total_services': total_services,
        'total_clients': total_clients,
        'total_employees': total_employees,
        'requests_by_month': requests_by_month,
        'month_labels': month_labels,
        'top_services': top_services,
        'monthly_chart': monthly_chart,
        'services_chart': services_chart,
        'status_chart': status_chart,
    }
    return render(request, 'main/statistics.html', context)
