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
import statistics

from .models import (
    News, Service, ServiceType, Device, DeviceType, Part, PartType,
    Client, Employee, Contract, Order, Vacancy, Review, PromoCode,
    Schedule, Term, CompanyInfo, CompanyHistory, FAQ, JobVacancy
)
from .forms import ReviewForm, ClientRegistrationForm, ServiceOrderForm, QuickClientProfileForm
from .utils import get_currency_rate, get_weather_data, get_text_calendar

logger = logging.getLogger(__name__)

def index(request):
    """Главная страница с последней новостью"""
    latest_news = News.objects.filter(is_published=True).first()
    company_info = CompanyInfo.objects.first()
    
    # Статистика для главной
    total_clients = Client.objects.count()
    total_orders = Order.objects.count()
    active_services = Service.objects.filter(is_active=True).count()
    
    # Внешние API
    currency_rate = get_currency_rate()
    weather = get_weather_data()
    
    # Календарь
    now = timezone.now()
    text_calendar = get_text_calendar(now.year, now.month)
    
    context = {
        'latest_news': latest_news,
        'company_info': company_info,
        'total_clients': total_clients,
        'total_orders': total_orders,
        'active_services': active_services,
        'currency_rate': currency_rate,
        'weather': weather,
        'text_calendar': text_calendar,
        'current_date': now.strftime('%d/%m/%Y'),
    }
    
    logger.info(f"Главная страница просмотрена пользователем {request.user}")
    return render(request, 'main/index.html', context)

def about_company(request):
    """О компании"""
    company = CompanyInfo.objects.first()
    history = CompanyHistory.objects.all().order_by('year')
    return render(request, 'main/about.html', {'company': company, 'history': history})

class NewsListView(ListView):
    """Список новостей"""
    model = News
    template_name = 'main/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10
    
    def get_queryset(self):
        return News.objects.filter(is_published=True)

class NewsDetailView(DetailView):
    """Детали новости"""
    model = News
    template_name = 'main/news_detail.html'

class ServiceListView(ListView):
    """Список услуг с фильтрацией"""
    model = Service
    template_name = 'main/service_list_simple.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True)
        
        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(service_type_id=category)
        
        # Фильтрация по минимальной цене
        min_price = self.request.GET.get('min_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        # Фильтрация по максимальной цене
        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        # Поиск по названию
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.select_related('service_type')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_types'] = ServiceType.objects.all()
        context['current_category'] = self.request.GET.get('category', '')
        context['current_min_price'] = self.request.GET.get('min_price', '')
        context['current_max_price'] = self.request.GET.get('max_price', '')
        context['current_search'] = self.request.GET.get('search', '')
        return context

def terms_list(request):
    """Словарь терминов (FAQ)"""
    terms = Term.objects.all()
    return render(request, 'main/terms_list.html', {'terms': terms})

def contacts(request):
    """Контакты - сотрудники"""
    employees = Employee.objects.all()
    return render(request, 'main/contacts.html', {'employees': employees})

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
    # Проверяем, является ли пользователь клиентом
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
    """Создание профиля клиента для авторизованного пользователя"""
    # Проверяем, что у пользователя еще нет профиля клиента
    if hasattr(request.user, 'client'):
        messages.info(request, 'У вас уже есть профиль клиента.')
        return redirect('main:client_dashboard')
    
    if request.method == 'POST':
        form = QuickClientProfileForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            messages.success(request, 'Профиль клиента успешно создан!')
            return redirect('main:add_review')
    else:
        form = QuickClientProfileForm()
    
    return render(request, 'main/create_client_profile.html', {'form': form})

@login_required
def client_dashboard(request):
    """Личный кабинет клиента"""
    try:
        client = Client.objects.get(user=request.user)
        orders = Order.objects.filter(contract__client=client).select_related('service', 'contract')
        contracts = Contract.objects.filter(client=client)
        
        # Доступные промокоды
        now = timezone.now()
        available_promocodes = PromoCode.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        )
        
        context = {
            'client': client,
            'orders': orders,
            'contracts': contracts,
            'available_promocodes': available_promocodes,
        }
        
        return render(request, 'main/client_dashboard.html', context)
    except Client.DoesNotExist:
        messages.error(request, 'Профиль клиента не найден')
        return redirect('index')

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

def faq_list(request):
    """Страница с часто задаваемыми вопросами"""
    # Получаем все активные FAQ, группируя по категориям
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order', 'date_added')
    
    # Группируем FAQ по категориям
    faq_by_category = {}
    for faq in faqs:
        category_name = faq.get_category_display()
        if category_name not in faq_by_category:
            faq_by_category[category_name] = []
        faq_by_category[category_name].append(faq)
    
    # Статистика
    total_questions = faqs.count()
    categories_count = len(faq_by_category)
    
    context = {
        'faq_by_category': faq_by_category,
        'total_questions': total_questions,
        'categories_count': categories_count,
        'page_title': 'Часто задаваемые вопросы'
    }
    
    return render(request, 'main/faq_list.html', context)
