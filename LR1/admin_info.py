#!/usr/bin/env python
"""
Быстрый вход в админ-панель
"""
import os
import sys
import django

# Настройка Django
sys.path.append('/Users/ksenianovak/Desktop/qqq')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_website.settings')
django.setup()

from django.contrib.auth import get_user_model

def show_admin_info():
    """Показать информацию для входа в админ-панель"""
    User = get_user_model()
    
    print("=== Информация для входа в админ-панель ===\n")
    
    # Найти всех админов
    admins = User.objects.filter(is_superuser=True)
    
    if admins.exists():
        print("Доступные суперпользователи:")
        for admin in admins:
            print(f"\n👤 Пользователь: {admin.username}")
            print(f"   📧 Email: {admin.email}")
            print(f"   ✅ Активен: {'Да' if admin.is_active else 'Нет'}")
            print(f"   🛡️  Суперпользователь: {'Да' if admin.is_superuser else 'Нет'}")
            print(f"   📅 Последний вход: {admin.last_login or 'Никогда'}")
        
        print(f"\n🔐 Быстрый вход с паролем 'admin123':")
        print(f"   Логин: admin")
        print(f"   Пароль: admin123")
        
        print(f"\n🌐 Доступные админ-панели:")
        print(f"   • Основная админка: http://127.0.0.1:8000/admin/")
        print(f"   • Мастер-панель: http://127.0.0.1:8000/master/")
        print(f"   • Кастомная админка: http://127.0.0.1:8000/custom-admin/")
        print(f"   • Django админка: http://127.0.0.1:8000/django-admin/")
        print(f"   • Админ-дашборд: http://127.0.0.1:8000/admin-dashboard/")
        print(f"   • Отчёты: http://127.0.0.1:8000/admin/reports/")
        
    else:
        print("❌ Суперпользователи не найдены!")
        print("Запустите setup_admin_quick.py для создания администратора")
    
    # Показать обычных сотрудников
    staff = User.objects.filter(is_staff=True, is_superuser=False)
    if staff.exists():
        print(f"\n👥 Сотрудники (is_staff=True):")
        for s in staff:
            print(f"   • {s.username} ({s.email})")

if __name__ == "__main__":
    show_admin_info()
