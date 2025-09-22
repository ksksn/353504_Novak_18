import requests
import calendar
from datetime import datetime
import logging
from django.db.models import Avg, Count, Sum
from .models import Client, Service, Order

logger = logging.getLogger(__name__)

def get_currency_rate():
    """Получение курса валют с API НБ РБ"""
    try:
        response = requests.get('https://api.nbrb.by/api/exrates/rates/USD?parammode=2', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('Cur_OfficialRate')
    except Exception as e:
        logger.error(f"Ошибка получения курса валют: {e}")
    return None

def get_weather_data():
    """Получение данных о погоде (заглушка)"""
    try:
        # Заглушка для демонстрации (в реальном проекте нужен API ключ)
        return 15  # Примерная температура
    except Exception as e:
        logger.error(f"Ошибка получения данных о погоде: {e}")
    return None

def get_text_calendar(year, month):
    """Получение текстового календаря"""
    try:
        return calendar.month(year, month)
    except Exception as e:
        logger.error(f"Ошибка генерации календаря: {e}")
        return "Ошибка календаря"

def get_client_statistics():
    """Статистика по клиентам"""
    try:
        return {
            'total_count': Client.objects.count(),
            'vip_count': Client.objects.filter(is_vip=True).count(),
            'avg_age': Client.objects.aggregate(avg_age=Avg('birth_date'))['avg_age'],
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики клиентов: {e}")
        return {}

def get_service_statistics():
    """Статистика по услугам"""
    try:
        return {
            'total_count': Service.objects.count(),
            'active_count': Service.objects.filter(is_active=True).count(),
            'avg_price': Service.objects.aggregate(avg_price=Avg('price'))['avg_price'],
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики услуг: {e}")
        return {}
