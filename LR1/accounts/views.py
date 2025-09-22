from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from main.forms import ClientRegistrationForm, UserProfileUpdateForm, ClientProfileUpdateForm
import logging

logger = logging.getLogger(__name__)

def register_client(request):
    """Регистрация клиента"""
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                
                # Автоматически логиним пользователя после регистрации
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Добро пожаловать, {username}! Регистрация прошла успешно.')
                    logger.info(f"Новый клиент зарегистрирован и вошел в систему: {username}")
                    # Перенаправляем на страницу услуг
                    return redirect('main:service_list')
                else:
                    messages.success(request, f'Аккаунт создан для {username}! Теперь можете войти в систему.')
                    return redirect('accounts:login')
            except Exception as e:
                logger.error(f"Ошибка при регистрации пользователя: {e}")
                messages.error(request, 'Произошла ошибка при регистрации. Попробуйте еще раз.')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ClientRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """Вход в систему"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        form.fields['username'].widget.attrs.update({'class': 'form-control'})
        form.fields['password'].widget.attrs.update({'class': 'form-control'})
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                logger.info(f"Пользователь {username} вошел в систему")
                messages.success(request, f'Добро пожаловать, {user.get_full_name() or username}!')
                
                if user.is_superuser:
                    return redirect('accounts:profile')
                elif hasattr(user, 'employee'):
                    return redirect('main:master_dashboard')
                elif hasattr(user, 'client'):
                    return redirect('main:client_dashboard')
                else:
                    messages.info(request, 'Добро пожаловать! Для полного функционала сайта рекомендуем завершить регистрацию как клиент.')
                    return redirect('main:index')
            else:
                messages.error(request, 'Неверный логин или пароль.')
                logger.warning(f"Неудачная попытка входа для пользователя: {username}")
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
            logger.warning(f"Ошибки в форме входа: {form.errors}")
    else:
        form = AuthenticationForm()
        form.fields['username'].widget.attrs.update({'class': 'form-control'})
        form.fields['password'].widget.attrs.update({'class': 'form-control'})
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile(request):
    """Профиль пользователя"""
    context = {}
    
    if hasattr(request.user, 'client'):
        context['user_type'] = 'client'
        context['profile'] = request.user.client
    elif hasattr(request.user, 'employee'):
        context['user_type'] = 'employee'
        context['profile'] = request.user.employee
    else:
        context['user_type'] = 'admin'
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Редактирование профиля пользователя"""
    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, instance=request.user, user_id=request.user.id)
        
        # Определяем, есть ли у пользователя профиль клиента
        client_form = None
        if hasattr(request.user, 'client'):
            client_form = ClientProfileUpdateForm(request.POST, instance=request.user.client)
        
        # Валидация форм
        user_form_valid = user_form.is_valid()
        client_form_valid = client_form.is_valid() if client_form else True
        
        if user_form_valid and client_form_valid:
            try:
                # Сохраняем пользователя
                user_form.save()
                logger.info(f"Пользователь {request.user.username} обновил свой профиль")
                
                # Сохраняем профиль клиента, если он есть
                if client_form:
                    client_form.save()
                    logger.info(f"Обновлен профиль клиента для пользователя {request.user.username}")
                
                messages.success(request, 'Профиль успешно обновлен!')
                return redirect('accounts:profile')
                
            except Exception as e:
                logger.error(f"Ошибка при обновлении профиля пользователя {request.user.username}: {e}")
                messages.error(request, 'Произошла ошибка при сохранении. Попробуйте еще раз.')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        user_form = UserProfileUpdateForm(instance=request.user, user_id=request.user.id)
        client_form = ClientProfileUpdateForm(instance=request.user.client) if hasattr(request.user, 'client') else None
    
    context = {
        'user_form': user_form,
        'client_form': client_form,
        'has_client_profile': hasattr(request.user, 'client'),
    }
    
    return render(request, 'accounts/edit_profile.html', context)
