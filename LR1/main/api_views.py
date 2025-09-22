from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg
import logging
from django.http import JsonResponse
from django.db.models import F
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from .image_api import get_news_image, get_predefined_news_images
import random

try:
    from .models import (
        Service, ServiceType, Order, Client, Contract, Device, Part, Review, Repair, SparePart, RepairSparePart, News, Category, Tag
    )
    from .serializers import (
        ServiceSerializer, ServiceTypeSerializer, OrderSerializer, 
        ClientSerializer, ContractSerializer, DeviceSerializer, 
        PartSerializer, ReviewSerializer
    )
    from .utils import get_client_statistics, get_service_statistics
except ImportError as e:
    # Создаем заглушки для отсутствующих моделей
    logger = logging.getLogger(__name__)
    logger.warning(f"Import error: {e}")
    
    # Минимальные заглушки для работы сервера
    class Service: pass
    class ServiceType: pass
    class Order: pass
    class Client: pass
    class Contract: pass
    class Device: pass
    class Part: pass
    class Review: pass
    class Repair: pass
    class SparePart: pass
    class RepairSparePart: pass
    class News: pass
    class Category: pass
    class Tag: pass

logger = logging.getLogger(__name__)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение только владельцу объекта или только чтение"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Услуги - только чтение для всех"""
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service_type', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']

class ServiceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Типы услуг - только чтение"""
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer

class OrderViewSet(viewsets.ModelViewSet):
    """Заказы - только для авторизованных пользователей"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'service']
    ordering_fields = ['created_at', 'total_sum']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        elif hasattr(user, 'client'):
            return Order.objects.filter(contract__client=user.client)
        elif hasattr(user, 'employee'):
            return Order.objects.filter(contract__employee=user.employee)
        return Order.objects.none()

class ClientViewSet(viewsets.ModelViewSet):
    """Клиенты - только для персонала"""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    ordering_fields = ['user__username', 'registration_date']

class ContractViewSet(viewsets.ModelViewSet):
    """Договоры - ограниченный доступ"""
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_completed', 'date_signed']
    ordering_fields = ['date_signed', 'total_sum']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Contract.objects.all()
        elif hasattr(user, 'client'):
            return Contract.objects.filter(client=user.client)
        elif hasattr(user, 'employee'):
            return Contract.objects.filter(employee=user.employee)
        return Contract.objects.none()

class DeviceViewSet(viewsets.ModelViewSet):
    """Устройства - только для персонала и владельцев"""
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Device.objects.all()
        elif hasattr(user, 'client'):
            return Device.objects.filter(client=user.client)
        return Device.objects.none()

class PartViewSet(viewsets.ReadOnlyModelViewSet):
    """Запчасти - только чтение"""
    queryset = Part.objects.filter(in_stock__gt=0)
    serializer_class = PartSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['part_type', 'price']
    search_fields = ['name']
    ordering_fields = ['name', 'price']

class ReviewViewSet(viewsets.ModelViewSet):
    """Отзывы"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating']

    def get_queryset(self):
        return Review.objects.filter(is_moderated=True)

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'client'):
            serializer.save(client=self.request.user.client)

class StatisticsAPIView(APIView):
    """API для статистики - только для персонала"""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        try:
            client_stats = get_client_statistics()
            service_stats = get_service_statistics()
            
            data = {
                'clients': client_stats,
                'services': service_stats,
                'orders': {
                    'total_count': Order.objects.count(),
                    'completed_count': Order.objects.filter(status='completed').count(),
                    'total_revenue': Order.objects.aggregate(Sum('total_sum'))['total_sum__sum'] or 0,
                    'avg_order_value': Order.objects.aggregate(Avg('total_sum'))['total_sum__avg'] or 0,
                }
            }
            
            logger.info(f"Статистика запрошена пользователем {request.user}")
            return Response(data)
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return Response(
                {'error': 'Ошибка получения статистики'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@staff_member_required
def spare_parts_by_category(request):
    category = request.GET.get('category')
    parts = SparePart.objects.all()
    
    if category:
        parts = parts.filter(category=category)
    
    data = list(parts.values('id', 'name', 'category', 'price', 'quantity_in_stock'))
    return JsonResponse({'spare_parts': data})

@staff_member_required
def repair_cost_calculation(request, repair_id):
    try:
        repair = Repair.objects.get(id=repair_id)
        spare_parts_cost = RepairSparePart.objects.filter(repair=repair).aggregate(
            total=Sum(F('quantity') * F('spare_part__price'))
        )['total'] or 0
        
        data = {
            'repair_id': repair.id,
            'labor_cost': float(repair.labor_cost),
            'spare_parts_cost': float(spare_parts_cost),
            'total_cost': float(repair.total_cost),
            'spare_parts': list(
                RepairSparePart.objects.filter(repair=repair).values(
                    'spare_part__name', 'quantity', 'spare_part__price'
                )
            )
        }
        return JsonResponse(data)
    except Repair.DoesNotExist:
        return JsonResponse({'error': 'Ремонт не найден'}, status=404)

@staff_member_required
def client_summary(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
        repairs = Repair.objects.filter(client=client)
        
        data = {
            'client_id': client.id,
            'client_name': client.name,
            'total_repairs': repairs.count(),
            'total_spent': float(repairs.aggregate(Sum('total_cost'))['total_cost__sum'] or 0),
            'repairs': list(repairs.values(
                'id', 'device__brand', 'device__model', 
                'status', 'total_cost', 'created_at'
            ))
        }
        return JsonResponse(data)
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Клиент не найден'}, status=404)

@staff_member_required
def yearly_statistics(request):
    year = request.GET.get('year')
    repairs = Repair.objects.all()
    
    if year:
        repairs = repairs.filter(created_at__year=year)
    
    stats = repairs.extra(
        select={'year': 'EXTRACT(year FROM created_at)'}
    ).values('year').annotate(
        total_repairs=Count('id'),
        total_revenue=Sum('total_cost')
    ).order_by('-year')
    
    return JsonResponse({'statistics': list(stats)})

@staff_member_required
def get_spare_part_price(request, spare_part_id):
    """API для получения цены запчасти (для админки)"""
    try:
        spare_part = SparePart.objects.get(id=spare_part_id)
        return JsonResponse({
            'price': float(spare_part.price),
            'name': spare_part.name,
            'stock': spare_part.quantity_in_stock
        })
    except SparePart.DoesNotExist:
        return JsonResponse({'error': 'Запчасть не найдена'}, status=404)

@staff_member_required
def get_service_price(request, service_id):
    """API для получения цены услуги (для админки)"""
    try:
        service = Service.objects.get(id=service_id)
        return JsonResponse({
            'price': float(service.price),
            'name': service.name,
            'is_active': service.is_active
        })
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Услуга не найдена'}, status=404)


class NewsWithImagesAPIView(APIView):
    """API для создания новостей с изображениями из внешних API"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Создает новость с изображением из API"""
        try:
            data = request.data
            
            # Проверяем обязательные поля
            title = data.get('title')
            if not title:
                return Response({'error': 'Поле title обязательно'}, status=status.HTTP_400_BAD_REQUEST)
            
            short_description = data.get('short_description', '')
            content = data.get('content', '')
            category_name = data.get('category', 'Новости компании')
            tag_names = data.get('tags', [])
            image_category = data.get('image_category', 'technology')
            
            # Получаем или создаем автора
            author = request.user
            
            # Получаем или создаем категорию
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Категория {category_name}'}
            )
            
            # Получаем изображение из API
            image_url = None
            try:
                image_url = get_news_image(image_category)
                if not image_url:
                    # Используем предопределенные изображения как fallback
                    predefined_images = get_predefined_news_images()
                    image_url = random.choice(predefined_images)
            except Exception as e:
                # Используем предопределенные изображения при ошибке
                predefined_images = get_predefined_news_images()
                image_url = random.choice(predefined_images)
            
            # Создаем новость
            news = News.objects.create(
                title=title,
                short_description=short_description,
                content=content,
                image_url=image_url,
                author=author,
                category=category,
                is_published=True
            )
            
            # Добавляем теги
            if tag_names:
                tags = []
                for tag_name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    tags.append(tag)
                news.tags.set(tags)
            
            return Response({
                'success': True,
                'message': 'Новость успешно создана',
                'news': {
                    'id': news.id,
                    'title': news.title,
                    'short_description': news.short_description,
                    'image_url': news.image_url,
                    'created_at': news.created_at.isoformat(),
                    'category': news.category.name if news.category else None,
                    'tags': [tag.name for tag in news.tags.all()],
                    'url': f'/news/{news.id}/'
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Ошибка при создании новости: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Получает список доступных категорий изображений и пример URL"""
        try:
            # Получаем пример изображения
            example_image = get_news_image('technology')
            
            return Response({
                'available_categories': [
                    'technology', 'repair', 'service', 'news', 'mobile', 'computer'
                ],
                'example_image_url': example_image,
                'predefined_images': get_predefined_news_images()[:3],  # Показываем только первые 3
                'usage': {
                    'create_news': 'POST /api/news-with-images/',
                    'required_fields': ['title'],
                    'optional_fields': ['short_description', 'content', 'category', 'tags', 'image_category']
                }
            })
            
        except Exception as e:
            return Response({
                'error': f'Ошибка при получении информации: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickNewsAPIView(APIView):
    """API для быстрого создания новостей с готовыми шаблонами"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Создает новость на основе выбранного шаблона"""
        try:
            template_type = request.data.get('template')
            custom_data = request.data.get('custom_data', {})
            
            templates = {
                'repair_news': {
                    'title': 'Новое оборудование для ремонта',
                    'short_description': 'Приобрели современное оборудование для более качественного ремонта.',
                    'content': '''В нашем сервисном центре появилось новое высокотехнологичное оборудование.

Благодаря новому оборудованию мы можем:
• Выполнять ремонт на компонентном уровне
• Восстанавливать разъемы любой сложности  
• Ремонтировать устройства после попадания жидкости
• Заменять процессоры и микросхемы памяти

Все работы выполняются с гарантией качества и в кратчайшие сроки.''',
                    'category': 'Техника',
                    'tags': ['Ремонт', 'Техника'],
                    'image_category': 'repair'
                },
                'discount_news': {
                    'title': 'Специальная акция - скидки на ремонт',
                    'short_description': 'Действуют специальные цены на ремонт популярных устройств.',
                    'content': '''Уважаемые клиенты! 

Рады сообщить о запуске новой акции - скидки на ремонт устройств популярных марок.

Условия акции:
• Скидка действует на выбранные услуги
• Не суммируется с другими скидками
• Требуется предварительная запись
• Гарантия на выполненные работы - 6 месяцев

Записаться можно по телефону или через форму на сайте.''',
                    'category': 'Акции',
                    'tags': ['Акции', 'Ремонт'],
                    'image_category': 'service'
                },
                'service_news': {
                    'title': 'Расширение сервисных возможностей',
                    'short_description': 'Добавили новые услуги для лучшего обслуживания клиентов.',
                    'content': '''Наша команда расширила список доступных услуг!

Новые возможности:
• Экспресс-диагностика устройств
• Выездной ремонт на дом
• Корпоративное обслуживание
• Консультации по выбору техники

Мы продолжаем развиваться, чтобы обеспечить вам лучший сервис!''',
                    'category': 'Сервис',
                    'tags': ['Сервис'],
                    'image_category': 'service'
                }
            }
            
            if template_type not in templates:
                return Response({
                    'error': 'Неизвестный шаблон',
                    'available_templates': list(templates.keys())
                }, status=status.HTTP_400_BAD_REQUEST)
            
            template = templates[template_type]
            
            # Применяем пользовательские данные поверх шаблона
            for key, value in custom_data.items():
                if key in template:
                    template[key] = value
            
            # Создаем новость через основной API
            request.data = template
            news_api = NewsWithImagesAPIView()
            return news_api.post(request)
            
        except Exception as e:
            return Response({
                'error': f'Ошибка при создании новости: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Получает доступные шаблоны новостей"""
        return Response({
            'templates': {
                'repair_news': 'Новость о ремонтном оборудовании',
                'discount_news': 'Новость об акциях и скидках', 
                'service_news': 'Новость о сервисных возможностях'
            },
            'usage': 'POST /api/quick-news/ с параметром template и опциональным custom_data'
        })
