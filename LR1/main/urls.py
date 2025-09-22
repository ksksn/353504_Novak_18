from django.urls import path
from . import views
from . import views_simple

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about_company, name='about'),
    
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('create-news-with-images/', views.create_news_with_images, name='create_news_with_images'),
    
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('terms/', views.terms_list, name='terms_list'),
    path('faq/', views.faq_list, name='faq_list'),
    path('contacts/', views.contacts, name='contacts'),
    path('company-policy/', views.company_policy, name='company_policy'),
    path('vacancies/', views.vacancies_list, name='vacancies'),
    path('reviews/', views.reviews_list, name='reviews_list'),
    path('reviews/add/', views.add_review, name='add_review'),
    path('create-client-profile/', views.create_client_profile, name='create_client_profile'),
    path('promocodes/', views.promocodes_list, name='promocodes'),
    
    path('dashboard/client/', views_simple.client_dashboard, name='client_dashboard'),
    path('dashboard/master/', views.master_dashboard, name='master_dashboard'),
    path('statistics/', views.statistics, name='statistics'),
    
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:service_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('submit-request/', views.submit_service_request, name='submit_service_request'),
    path('service-requests/', views.service_requests_list, name='service_requests'),
    path('service-requests/<int:request_id>/', views.service_request_detail, name='service_request_detail'),
    
    path('admin/service-requests/', views.admin_service_requests, name='admin_service_requests'),
    path('admin/service-requests/<int:request_id>/', views.admin_service_request_detail, name='admin_service_request_detail'),
]
