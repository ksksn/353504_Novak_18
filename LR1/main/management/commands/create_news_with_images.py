"""
Django management команда для создания новостей с изображениями из API
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import News, Category, Tag
from main.image_api import get_news_image, get_predefined_news_images
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Создает новости с изображениями из API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Количество новостей для создания'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Удалить существующие новости перед созданием новых'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']

        if clear:
            News.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Существующие новости удалены')
            )

        # Получаем или создаем автора
        author, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Администратор',
                'last_name': 'Сайта',
                'email': 'admin@servicecenter.ru',
                'is_staff': True,
                'is_superuser': True
            }
        )

        # Получаем или создаем категории
        categories = []
        category_names = [
            ('Новости компании', 'Новости и события сервисного центра'),
            ('Техника', 'Новости о технике и гаджетах'),
            ('Ремонт', 'Информация о ремонте и обслуживании'),
            ('Акции', 'Специальные предложения и скидки')
        ]
        
        for name, description in category_names:
            category, _ = Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            categories.append(category)

        # Получаем или создаем теги
        tag_names = ['Ремонт', 'Техника', 'Сервис', 'Акции', 'Смартфоны', 'Компьютеры']
        tags = []
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)

        # Шаблоны новостей
        news_templates = [
            {
                'title': 'Новое оборудование для ремонта {}',
                'short_description': 'Приобрели современное оборудование для более качественного ремонта {}.',
                'content': '''В нашем сервисном центре появилось новое высокотехнологичное оборудование для ремонта {}.

Новая паяльная станция позволяет выполнять самые сложные микропайки с точностью до микрона. Это означает, что мы можем восстанавливать даже самые миниатюрные компоненты на материнских платах современных устройств.

Также установлен стереомикроскоп с увеличением до 45x, который обеспечивает идеальную видимость при работе с микросхемами и разъемами.

Благодаря новому оборудованию мы можем:
• Выполнять ремонт материнских плат на компонентном уровне
• Восстанавливать разъемы зарядки любой сложности  
• Ремонтировать устройства после попадания жидкости
• Заменять процессоры и микросхемы памяти

Все работы выполняются с гарантией качества и в кратчайшие сроки.''',
                'category_type': 'repair',
                'tag_keywords': ['Ремонт', 'Техника']
            },
            {
                'title': 'Акция: скидка {}% на замену {}',
                'short_description': 'Специальная цена на замену {} для всех моделей устройств.',
                'content': '''Уважаемые клиенты! 

Рады сообщить о запуске новой акции - скидка {}% на замену {} для устройств всех популярных марок.

Акция действует в течение месяца и распространяется на:
• iPhone всех моделей
• Samsung Galaxy серии S, Note, A
• Xiaomi, Huawei, Honor
• OnePlus, Google Pixel
• И многие другие бренды

Используем только оригинальные и высококачественные совместимые компоненты. Все запчасти сертифицированы и имеют гарантию.

Условия акции:
• Скидка действует только на работы по замене
• Не суммируется с другими скидками
• Требуется предварительная запись
• Гарантия на выполненные работы - 6 месяцев

Записаться можно по телефону или через форму на сайте.''',
                'category_type': 'mobile',
                'tag_keywords': ['Акции', 'Ремонт']
            },
            {
                'title': 'Расширение штата: новые мастера в команде',
                'short_description': 'К нам присоединились опытные специалисты по ремонту техники.',
                'content': '''Наша команда пополнилась новыми талантливыми специалистами!

Встречайте наших новых мастеров:

**Алексей Петров** - специалист по ремонту ноутбуков
• Опыт работы более 8 лет
• Сертификат Lenovo Authorized Service
• Специализация: замена матриц, клавиатур, системы охлаждения
• Ремонт материнских плат ноутбуков

**Мария Сидорова** - мастер по ремонту ПК и серверного оборудования  
• Опыт работы 6 лет
• Сертификат Microsoft Hardware Specialist
• Специализация: диагностика и ремонт системных блоков
• Настройка и обслуживание серверов

Благодаря расширению команды мы можем:
• Сократить время ожидания ремонта
• Принимать больше заказов
• Предлагать более широкий спектр услуг
• Работать с корпоративными клиентами

Наши новые специалисты уже приступили к работе и готовы помочь вам!''',
                'category_type': 'service',
                'tag_keywords': ['Сервис']
            },
            {
                'title': 'Открытие экспресс-ремонта {}',
                'short_description': 'Теперь ремонтируем {} за 24 часа.',
                'content': '''Рады объявить об открытии нового направления - экспресс-ремонт {}!

Что мы теперь ремонтируем:

**Основные услуги:**
• Замена дисплеев и тачскринов
• Ремонт разъемов зарядки
• Замена батарей и аккумуляторов
• Восстановление после попадания влаги
• Прошивка и разблокировка

**Особенности экспресс-сервиса:**
• Диагностика в течение 2 часов
• Ремонт за 24 часа (в 90% случаев)
• Гарантия на работы 3 месяца
• Специальные цены на массовые поломки
• Возможность ремонта в присутствии клиента

Мы понимаем, как важны для вас эти устройства в повседневной жизни, поэтому постарались сделать процесс ремонта максимально быстрым и удобным.

Принимаем заказы ежедневно с 9:00 до 20:00.''',
                'category_type': 'technology',
                'tag_keywords': ['Сервис', 'Техника']
            },
            {
                'title': 'Программа лояльности для постоянных клиентов',
                'short_description': 'Запускаем систему накопительных скидок и бонусов.',
                'content': '''Мы ценим доверие наших клиентов и запускаем программу лояльности "Верный клиент"!

**Как это работает:**

🥉 **Бронзовый статус** (от 3000 руб. за год)
• Скидка 5% на все услуги
• Приоритетная запись на ремонт
• SMS-уведомления о готовности

🥈 **Серебряный статус** (от 8000 руб. за год)  
• Скидка 10% на все услуги
• Бесплатная диагностика
• Продление гарантии до 1 года
• Скидка 15% на запчасти

🥇 **Золотой статус** (от 15000 руб. за год)
• Скидка 15% на все услуги  
• Персональный менеджер
• Выезд курьера бесплатно
• Скидка 25% на запчасти
• Приоритетное обслуживание

**Дополнительные бонусы:**
• За каждый отзыв - скидка 200 руб. на следующий ремонт
• Приведи друга - получи 500 руб. на счет
• В день рождения - скидка 20% на любые услуги

Программа стартует с 1 числа следующего месяца. Подключайтесь и экономьте!''',
                'category_type': 'service',
                'tag_keywords': ['Акции', 'Сервис']
            }
        ]

        # Данные для заполнения шаблонов
        device_types = ['смартфонов', 'ноутбуков', 'планшетов', 'компьютеров']
        repair_parts = ['экранов', 'батарей', 'разъемов', 'клавиатур']
        discount_values = [15, 20, 25, 30]

        created_count = 0
        predefined_images = get_predefined_news_images()

        for i in range(count):
            # Выбираем случайный шаблон
            template = random.choice(news_templates)
            
            # Заполняем шаблон данными
            if '{}' in template['title']:
                if 'скидка' in template['title']:
                    discount = random.choice(discount_values)
                    part = random.choice(repair_parts)
                    title = template['title'].format(discount, part)
                    short_description = template['short_description'].format(part)
                    content = template['content'].format(discount, part)
                else:
                    device = random.choice(device_types)
                    title = template['title'].format(device)
                    short_description = template['short_description'].format(device)
                    content = template['content'].format(device)
            else:
                title = template['title']
                short_description = template['short_description']
                content = template['content']

            # Выбираем категорию
            category = random.choice(categories)

            # Выбираем теги
            available_tags = [tag for tag in tags if tag.name in template['tag_keywords']]
            if not available_tags:
                available_tags = random.sample(tags, min(2, len(tags)))

            # Получаем изображение из API
            image_url = None
            
            # Сначала пытаемся получить изображение из API
            try:
                image_url = get_news_image(template['category_type'])
                if not image_url:
                    # Используем предопределенные изображения как fallback
                    image_url = random.choice(predefined_images)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Ошибка при получении изображения из API: {e}')
                )
                # Используем предопределенные изображения как fallback
                image_url = random.choice(predefined_images)

            # Вычисляем дату создания (от 1 до 30 дней назад)
            days_ago = random.randint(1, 30)
            created_date = datetime.now() - timedelta(days=days_ago)

            # Создаем новость
            news = News.objects.create(
                title=title,
                short_description=short_description,
                content=content,
                image_url=image_url,
                author=author,
                category=category,
                is_published=True,
                created_at=created_date
            )

            # Добавляем теги
            news.tags.set(available_tags)

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'✓ Создана новость: {news.title}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\nИтого создано новостей: {created_count}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Всего новостей в базе: {News.objects.count()}')
        )
