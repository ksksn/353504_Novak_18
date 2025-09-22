from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'services', api_views.ServiceViewSet)
router.register(r'service-types', api_views.ServiceTypeViewSet)
router.register(r'orders', api_views.OrderViewSet, basename='order')
router.register(r'clients', api_views.ClientViewSet)
router.register(r'contracts', api_views.ContractViewSet, basename='contract')
router.register(r'devices', api_views.DeviceViewSet, basename='device')
router.register(r'parts', api_views.PartViewSet)
router.register(r'reviews', api_views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('statistics/', api_views.StatisticsAPIView.as_view(), name='api-statistics'),
    path('spare-parts/', api_views.spare_parts_by_category, name='api_spare_parts'),
    path('repair-cost/<int:repair_id>/', api_views.repair_cost_calculation, name='api_repair_cost'),
    path('client-summary/<int:client_id>/', api_views.client_summary, name='api_client_summary'),
    path('yearly-stats/', api_views.yearly_statistics, name='api_yearly_stats'),
    # API для админки
    path('admin/spare-part/<int:spare_part_id>/', api_views.get_spare_part_price, name='api_admin_spare_part_price'),
    path('admin/service/<int:service_id>/', api_views.get_service_price, name='api_admin_service_price'),
    # API для новостей с изображениями
    path('news-with-images/', api_views.NewsWithImagesAPIView.as_view(), name='api_news_with_images'),
    path('quick-news/', api_views.QuickNewsAPIView.as_view(), name='api_quick_news'),
]
