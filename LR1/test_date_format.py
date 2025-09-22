#!/usr/bin/env python
"""
Тестовый скрипт для проверки работы форм с новым форматом даты
"""
import os
import sys
import django
from datetime import date

# Настройка Django
sys.path.append('/Users/ksenianovak/Downloads/LR5')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_website.settings')
django.setup()

from main.forms import ClientRegistrationForm, QuickClientProfileForm

def test_client_registration_form():
    """Тест формы регистрации клиента"""
    print("=== Тест ClientRegistrationForm ===")
    
    # Тестовые данные
    form_data = {
        'username': 'testuser',
        'first_name': 'Тест',
        'last_name': 'Пользователь',
        'email': 'test@example.com',
        'password1': 'testpassword123',
        'password2': 'testpassword123',
        'phone': '+375 (29) 123-45-67',
        'address': 'Тестовый адрес',
        'birth_date': '22.05.2006'  # Формат ДД.ММ.ГГГГ
    }
    
    form = ClientRegistrationForm(data=form_data)
    
    if form.is_valid():
        print("✅ Форма валидна с датой в формате ДД.ММ.ГГГГ")
        print(f"   Дата рождения: {form.cleaned_data['birth_date']}")
    else:
        print("❌ Форма невалидна:")
        for field, errors in form.errors.items():
            print(f"   {field}: {errors}")
    
    # Проверим также формат YYYY-MM-DD
    form_data['birth_date'] = '2006-05-22'
    form2 = ClientRegistrationForm(data=form_data)
    
    if form2.is_valid():
        print("✅ Форма валидна с датой в формате YYYY-MM-DD")
        print(f"   Дата рождения: {form2.cleaned_data['birth_date']}")
    else:
        print("❌ Форма невалидна с форматом YYYY-MM-DD:")
        for field, errors in form2.errors.items():
            print(f"   {field}: {errors}")

def test_quick_client_profile_form():
    """Тест быстрой формы создания профиля клиента"""
    print("\n=== Тест QuickClientProfileForm ===")
    
    # Тестовые данные
    form_data = {
        'phone': '+375 (29) 987-65-43',
        'address': 'Другой тестовый адрес',
        'birth_date': '15.08.1995'  # Формат ДД.ММ.ГГГГ
    }
    
    form = QuickClientProfileForm(data=form_data)
    
    if form.is_valid():
        print("✅ Форма валидна с датой в формате ДД.ММ.ГГГГ")
        print(f"   Дата рождения: {form.cleaned_data['birth_date']}")
    else:
        print("❌ Форма невалидна:")
        for field, errors in form.errors.items():
            print(f"   {field}: {errors}")

def test_age_validation():
    """Тест валидации возраста"""
    print("\n=== Тест валидации возраста ===")
    
    # Слишком молодой пользователь
    young_data = {
        'phone': '+375 (29) 111-22-33',
        'address': 'Адрес молодого пользователя',
        'birth_date': '01.01.2010'  # 15 лет
    }
    
    form = QuickClientProfileForm(data=young_data)
    if not form.is_valid() and 'birth_date' in form.errors:
        print("✅ Валидация возраста работает для молодых пользователей")
        print(f"   Ошибка: {form.errors['birth_date']}")
    else:
        print("❌ Валидация возраста не работает для молодых пользователей")
    
    # Слишком старый пользователь
    old_data = {
        'phone': '+375 (29) 444-55-66',
        'address': 'Адрес старого пользователя',
        'birth_date': '01.01.1900'  # 125 лет
    }
    
    form2 = QuickClientProfileForm(data=old_data)
    if not form2.is_valid() and 'birth_date' in form2.errors:
        print("✅ Валидация возраста работает для старых дат")
        print(f"   Ошибка: {form2.errors['birth_date']}")
    else:
        print("❌ Валидация возраста не работает для старых дат")

if __name__ == '__main__':
    test_client_registration_form()
    test_quick_client_profile_form()
    test_age_validation()
    print("\n=== Тестирование завершено ===")
