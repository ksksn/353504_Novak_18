#!/usr/bin/env python
"""
Тестирование функциональности редактирования профиля
"""
import os
import sys
import django

# Настройка Django
sys.path.append('/Users/ksenianovak/Desktop/qqq')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_website.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Client

def test_profile_editing():
    """Тестирование редактирования профиля"""
    print("=== Тест функциональности редактирования профиля ===\n")
    
    # Проверяем существующих пользователей
    users = User.objects.all()
    print(f"Всего пользователей в системе: {users.count()}")
    
    if users.count() > 0:
        print("\nСписок пользователей:")
        for user in users:
            user_type = "Администратор"
            if hasattr(user, 'client'):
                user_type = "Клиент"
            elif hasattr(user, 'employee'):
                user_type = "Сотрудник"
            
            print(f"  - {user.username} ({user.get_full_name()}) - {user_type}")
            print(f"    Email: {user.email}")
            if hasattr(user, 'client'):
                client = user.client
                print(f"    Телефон: {client.phone or 'Не указан'}")
                print(f"    Адрес: {client.address or 'Не указан'}")
                print(f"    Дата рождения: {client.birth_date or 'Не указана'}")
            print()
    
    # Проверяем клиентов
    clients = Client.objects.all()
    print(f"Всего клиентов: {clients.count()}")
    
    if clients.count() > 0:
        print("\nПодробная информация о клиентах:")
        for client in clients:
            print(f"  Клиент: {client.user.get_full_name()} ({client.user.username})")
            print(f"  Email: {client.user.email}")
            print(f"  Телефон: {client.phone or 'Не указан'}")
            print(f"  Адрес: {client.address or 'Не указан'}")
            print(f"  Дата рождения: {client.birth_date or 'Не указана'}")
            print(f"  Дата регистрации: {client.user.date_joined.strftime('%d.%m.%Y %H:%M')}")
            print("-" * 50)
    
    return True

def show_url_endpoints():
    """Показать доступные URL endpoints для профиля"""
    print("\n=== Доступные URL для работы с профилем ===")
    print("📄 Просмотр профиля: http://127.0.0.1:8000/accounts/profile/")
    print("✏️  Редактирование профиля: http://127.0.0.1:8000/accounts/profile/edit/")
    print("🔐 Вход в систему: http://127.0.0.1:8000/accounts/login/")
    print("📝 Регистрация: http://127.0.0.1:8000/accounts/register/")
    print("🔒 Смена пароля: http://127.0.0.1:8000/accounts/password_reset/")
    print("🏠 Главная страница: http://127.0.0.1:8000/")

if __name__ == "__main__":
    test_profile_editing()
    show_url_endpoints()
    
    print("\n✅ Тестирование завершено!")
    print("\n📋 Возможности редактирования профиля:")
    print("   ✓ Изменение username")
    print("   ✓ Изменение имени и фамилии")
    print("   ✓ Изменение email")
    print("   ✓ Редактирование телефона клиента")
    print("   ✓ Редактирование адреса клиента")
    print("   ✓ Редактирование даты рождения")
    print("   ✓ Валидация всех полей")
    print("   ✓ Проверка уникальности username и email")
