#!/usr/bin/env python
"""
Простой скрипт для создания/обновления администратора
"""
import os
import sys
import django

sys.path.append('/Users/ksenianovak/Desktop/qqq')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_website.settings')
django.setup()

from django.contrib.auth import get_user_model

def setup_admin():
    """Создание или обновление администратора"""
    User = get_user_model()
    
    print("=== Настройка администратора ===\n")
    
    # Проверяем существующих суперпользователей
    admins = User.objects.filter(is_superuser=True)
    print(f"Найдено суперпользователей: {admins.count()}")
    
    for admin in admins:
        print(f"  • {admin.username} ({admin.email}) - активен: {admin.is_active}")
    
    # Создаем или обновляем админа
    admin_username = 'admin'
    admin_email = 'admin@servicecenter.com'
    admin_password = 'admin123'
    
    admin, created = User.objects.get_or_create(
        username=admin_username,
        defaults={
            'email': admin_email,
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'first_name': 'Администратор',
            'last_name': 'Сервисного центра'
        }
    )
    
    # Устанавливаем пароль
    admin.set_password(admin_password)
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_active = True
    admin.save()
    
    if created:
        print(f"\n✅ Создан новый администратор:")
    else:
        print(f"\n✅ Обновлен существующий администратор:")
    
    print(f"   Логин: {admin_username}")
    print(f"   Пароль: {admin_password}")
    print(f"   Email: {admin_email}")
    print(f"   URL админки: http://127.0.0.1:8000/admin/")
    
    return True

if __name__ == "__main__":
    try:
        setup_admin()
        print("\n🎉 Администратор готов к работе!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
