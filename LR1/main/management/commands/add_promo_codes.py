from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.models import PromoCode

class Command(BaseCommand):
    help = 'Adds 10 promo codes to the database'

    def handle(self, *args, **kwargs):
        # Список промокодов с их описаниями и скидками
        promo_codes = [
            {
                'code': 'WELCOME10',
                'description': 'Скидка 10% для новых клиентов',
                'discount_percent': 10,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=30)
            },
            {
                'code': 'SUMMER20',
                'description': 'Летняя скидка 20%',
                'discount_percent': 20,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=60)
            },
            {
                'code': 'REPAIR15',
                'description': 'Скидка 15% на ремонт',
                'discount_percent': 15,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=45)
            },
            {
                'code': 'FIRST50',
                'description': 'Скидка 50% на первую услугу',
                'discount_percent': 50,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=15)
            },
            {
                'code': 'WEEKEND25',
                'description': 'Скидка 25% на услуги в выходные',
                'discount_percent': 25,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=90)
            },
            {
                'code': 'VIP30',
                'description': 'Скидка 30% для постоянных клиентов',
                'discount_percent': 30,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=120)
            },
            {
                'code': 'QUICK40',
                'description': 'Скидка 40% на срочный ремонт',
                'discount_percent': 40,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=30)
            },
            {
                'code': 'BULK20',
                'description': 'Скидка 20% при заказе нескольких услуг',
                'discount_percent': 20,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=60)
            },
            {
                'code': 'NEWYEAR35',
                'description': 'Новогодняя скидка 35%',
                'discount_percent': 35,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=90)
            },
            {
                'code': 'SPECIAL25',
                'description': 'Специальная скидка 25%',
                'discount_percent': 25,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=45)
            }
        ]

        # Создаем промокоды
        for promo in promo_codes:
            PromoCode.objects.get_or_create(
                code=promo['code'],
                defaults={
                    'description': promo['description'],
                    'discount_percent': promo['discount_percent'],
                    'valid_from': promo['valid_from'],
                    'valid_until': promo['valid_until'],
                    'is_active': True
                }
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created promo code: {promo["code"]}')
            ) 