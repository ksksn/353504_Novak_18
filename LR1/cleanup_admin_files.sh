#!/bin/bash
cd /Users/ksenianovak/Desktop/LR5/main/

# Удаляем все дополнительные админ-файлы
rm -f admin_views.py
rm -f admin_utils.py
rm -f admin_urls.py
rm -f admin_reports.py
rm -f admin_new.py
rm -f admin_master.py
rm -f admin_forms.py
rm -f admin_enhanced_actions.py
rm -f admin_actions.py

# Удаляем файлы из корневой папки проекта
cd /Users/ksenianovak/Desktop/LR5/
rm -f admin_info.py

# Удаляем проблемные миграции
cd /Users/ksenianovak/Desktop/LR5/main/migrations/
rm -f 0*.py
# Оставляем только __init__.py
touch __init__.py

echo "Удалены лишние админ-файлы и миграции"
echo "Теперь выполните:"
echo "1. python manage.py makemigrations main"
echo "2. python manage.py migrate"
