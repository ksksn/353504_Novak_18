#!/usr/bin/env python
"""
Скрипт для добавления фотографий к сотрудникам
"""
import os
import sys
import django
import requests
from pathlib import Path

sys.path.append('/Users/ksenianovak/Desktop/qqq')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_website.settings')
django.setup()

from main.models import Employee
from django.core.files.base import ContentFile
from django.conf import settings

def download_avatar_photo(gender='mixed', index=1):
    """Скачивание аватара с сервиса"""
    try:
        services = [
            f"https://randomuser.me/api/portraits/{'men' if index % 2 == 0 else 'women'}/{index}.jpg",
            f"https://i.pravatar.cc/300?img={index}",
            f"https://picsum.photos/300/300?random={index}",
        ]
        
        url = services[index % len(services)]
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return ContentFile(response.content)
        else:
            print(f"❌ Ошибка загрузки изображения: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при скачивании: {e}")
        return None

def create_placeholder_image(initials, index=1):
    """Создание изображения-заглушки с инициалами"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Создаем изображение 300x300
        size = 300
        colors = [
            (103, 126, 234),  # Синий
            (118, 75, 162),   # Фиолетовый
            (52, 152, 219),   # Голубой
            (46, 204, 113),   # Зеленый
            (230, 126, 34),   # Оранжевый
            (231, 76, 60),    # Красный
        ]
        
        color = colors[index % len(colors)]
        
        # Создаем изображение с градиентом
        img = Image.new('RGB', (size, size), color)
        draw = ImageDraw.Draw(img)
        
        # Пытаемся загрузить шрифт
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 120)
        except:
            font = ImageFont.load_default()
        
        # Добавляем инициалы в центр
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), initials, fill='white', font=font)
        
        # Сохраняем в BytesIO
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG', quality=95)
        img_io.seek(0)
        
        return ContentFile(img_io.getvalue())
        
    except ImportError:
        print("❌ Pillow не установлен. Устанавливаем...")
        os.system("pip install Pillow")
        return None
    except Exception as e:
        print(f"❌ Ошибка создания изображения: {e}")
        return None

def add_photos_to_employees():
    """Добавление фотографий к сотрудникам"""
    print("=== Добавление фотографий к сотрудникам ===\n")
    
    employees = Employee.objects.all()
    
    if not employees:
        print("❌ Сотрудники не найдены")
        return
    
    print(f"Найдено сотрудников: {employees.count()}")
    
    # Создаем папку для фотографий, если её нет
    media_root = Path(settings.MEDIA_ROOT)
    employees_dir = media_root / 'employees'
    employees_dir.mkdir(parents=True, exist_ok=True)
    
    for index, employee in enumerate(employees, 1):
        print(f"\n[{index}/{employees.count()}] Обработка: {employee.user.get_full_name()}")
        
        # Если у сотрудника уже есть фото, пропускаем
        if employee.photo and employee.photo.name:
            print("  ✓ Фото уже есть, пропускаем")
            continue
        
        # Создаем инициалы
        first_initial = employee.user.first_name[0] if employee.user.first_name else 'N'
        last_initial = employee.user.last_name[0] if employee.user.last_name else 'A'
        initials = f"{first_initial}{last_initial}"
        
        # Пытаемся скачать фото
        photo_content = download_avatar_photo(index=index)
        
        if not photo_content:
            # Создаем заглушку с инициалами
            photo_content = create_placeholder_image(initials, index)
        
        if photo_content:
            # Сохраняем фото
            filename = f"employee_{employee.id}_{employee.user.username}.jpg"
            employee.photo.save(filename, photo_content, save=True)
            print(f"  ✓ Фото добавлено: {filename}")
        else:
            print("  ❌ Не удалось создать фото")

def add_sample_employees():
    """Добавление примеров сотрудников, если их нет"""
    from django.contrib.auth.models import User
    from datetime import date
    
    if Employee.objects.count() > 0:
        print("Сотрудники уже есть в системе")
        return
    
    print("Создаем примеры сотрудников...")
    
    # Пример сотрудников
    sample_employees = [
        {
            'username': 'ivan_petrov',
            'first_name': 'Иван', 
            'last_name': 'Петров',
            'email': 'ivan@service.com',
            'position': 'manager',
            'phone': '+375 (29) 111-11-11',
            'description': 'Опытный менеджер по работе с клиентами'
        },
        {
            'username': 'maria_sidorova',
            'first_name': 'Мария',
            'last_name': 'Сидорова', 
            'email': 'maria@service.com',
            'position': 'technician',
            'phone': '+375 (29) 222-22-22',
            'description': 'Специалист по ремонту мобильных устройств'
        },
        {
            'username': 'alex_kozlov',
            'first_name': 'Александр',
            'last_name': 'Козлов',
            'email': 'alex@service.com', 
            'position': 'master',
            'phone': '+375 (29) 333-33-33',
            'description': 'Мастер по диагностике и ремонту'
        },
        {
            'username': 'elena_volkov',
            'first_name': 'Елена',
            'last_name': 'Волкова',
            'email': 'elena@service.com',
            'position': 'director',
            'phone': '+375 (29) 444-44-44',
            'description': 'Директор сервисного центра'
        }
    ]
    
    for emp_data in sample_employees:
        # Создаем пользователя
        user, created = User.objects.get_or_create(
            username=emp_data['username'],
            defaults={
                'first_name': emp_data['first_name'],
                'last_name': emp_data['last_name'],
                'email': emp_data['email'],
            }
        )
        
        if created:
            user.set_password('employee123')
            user.save()
        
        # Создаем сотрудника
        employee, created = Employee.objects.get_or_create(
            user=user,
            defaults={
                'position': emp_data['position'],
                'phone': emp_data['phone'],
                'email': emp_data['email'],
                'description': emp_data['description'],
                'birth_date': date(1990, 1, 1),
                'hire_date': date.today(),
                'salary': 1000.00
            }
        )
        
        if created:
            print(f"  ✓ Создан сотрудник: {user.get_full_name()}")

if __name__ == "__main__":
    # Сначала создаем сотрудников, если их нет
    add_sample_employees()
    
    # Затем добавляем фотографии
    add_photos_to_employees()
    
    print(f"\n✅ Обработка завершена!")
    print(f"Всего сотрудников: {Employee.objects.count()}")
    print(f"С фотографиями: {Employee.objects.exclude(photo='').count()}")
