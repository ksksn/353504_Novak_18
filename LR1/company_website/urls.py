from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from main.admin_new import admin_site
from main.admin_master import master_admin_site

urlpatterns = [
    path('admin/', admin_site.urls),  # Основная админка для суперпользователя
    path('master/', master_admin_site.urls),  # Админка для мастеров
    path('django-admin/', admin.site.urls),  # Оригинальная Django-админка (для отладки)
    path('custom-admin/', include('main.admin_urls')),  # Кастомная HTML админка
    path('', include('main.urls')),
    path('api/', include('main.api_urls')),
    path('accounts/', include('accounts.urls')),
    re_path(r'^privacy-policy/$', TemplateView.as_view(template_name='main/privacy_policy.html'), name='privacy_policy'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
