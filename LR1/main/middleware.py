from django.utils import timezone
import pytz
import logging

logger = logging.getLogger(__name__)

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Определяем часовой пояс пользователя
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
        
        # Логируем API запросы
        if request.path.startswith('/api/'):
            logger.info(f"API запрос: {request.method} {request.path} от {request.user}")
        
        response = self.get_response(request)
        return response
