#!/usr/bin/env python
"""
Скрипт для установки мастер-пароля администратора
"""
import os
import sys
import django

sys.path.append('/Users/ksenianovak/Desktop/qqq')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_website.settings')
django.setup()

from django.contrib.auth import get_user_model

def set_admin_password():
    """Установка мастер-пароля для администратора"""
    User = get_user_model()
    
    print("=== Установка мастер-пароля администратора ===\n")
    
    # Найти суперпользователя
    try:
        admin = User.objects.filter(is_superuser=True).first()
        if admin:
            print(f"✓ Найден суперпользователь: {admin.username}")
        else:
            print("❌ Суперпользователь не найден. Создаем нового...")
            username = input("Введите имя пользователя для администратора (по умолчанию 'admin'): ").strip() or 'admin'
            email = input("Введите email для администратора: ").strip()
            
            admin = User.objects.create_superuser(
                username=username,
                email=email,
                password='temp123'  # Временный пароль
            )
            print(f"✓ Создан новый суперпользователь: {admin.username}")
    
    except Exception as e:
        print(f"❌ Ошибка при работе с пользователем: {e}")
        return False
    
    # Установка нового пароля
    print(f"\nТекущий администратор: {admin.username}")
    
    # Предлагаемые варианты паролей
    suggested_passwords = [
        'admin123',
        'master2025',
        'service_center_admin',
        'SuperAdmin123!',
        'MasterPassword2025'
    ]
    
    print("\nПредлагаемые пароли:")
    for i, password in enumerate(suggested_passwords, 1):
        print(f"  {i}. {password}")
    
    print("  6. Ввести свой пароль")
    
    choice = input("\nВыберите вариант (1-6): ").strip()
    
    if choice == '6':
        password = input("Введите новый пароль: ").strip()
        if len(password) < 6:
            print("❌ Пароль должен содержать минимум 6 символов")
            return False
    elif choice in ['1', '2', '3', '4', '5']:
        password = suggested_passwords[int(choice) - 1]
    else:
        print("❌ Неверный выбор")
        return False
    
    # Установка пароля
    try:
        admin.set_password(password)
        admin.save()
        print(f"\n✅ Пароль успешно установлен для пользователя '{admin.username}'")
        print(f"📝 Данные для входа:")
        print(f"   Имя пользователя: {admin.username}")
        print(f"   Пароль: {password}")
        print(f"   URL админки: http://127.0.0.1:8000/admin/")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при установке пароля: {e}")
        return False

def show_current_admins():
    """Показать текущих администраторов"""
    User = get_user_model()
    
    print("\n=== Текущие администраторы ===")
    
    admins = User.objects.filter(is_superuser=True)
    
    if admins:
        for admin in admins:
            print(f"  • {admin.username} ({admin.email})")
            print(f"    Активен: {'Да' if admin.is_active else 'Нет'}")
            print(f"    Последний вход: {admin.last_login or 'Никогда'}")
            print()
    else:
        print("  Администраторы не найдены")

if __name__ == "__main__":
    show_current_admins()
    
    if input("\nХотите установить новый пароль? (y/n): ").lower() == 'y':
        set_admin_password()
    else:
        print("Операция отменена")
