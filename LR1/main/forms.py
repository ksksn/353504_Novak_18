from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review, Client, PassportData, Service, Order, Device, ServiceType
import re

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['service', 'rating', 'text']
        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-control'
            }),
            'rating': forms.Select(choices=Review.RATING_CHOICES, attrs={
                'class': 'form-control',
                'required': True
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Напишите ваш отзыв...',
                'required': True,
                'minlength': 10,
                'maxlength': 1000
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['service'].empty_label = "Общий отзыв о сервисе"
    
    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text) < 10:
            raise forms.ValidationError('Отзыв должен содержать минимум 10 символов')
        return text

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(
        max_length=20, 
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '+375 (29) XXX-XX-XX',
            'pattern': r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$'
        }),
        help_text="Формат: +375 (29) XXX-XX-XX"
    )
    address = forms.CharField(
        max_length=255, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш адрес'})
    )
    birth_date = forms.DateField(
        required=True,
        input_formats=['%d.%m.%Y', '%Y-%m-%d'],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ДД.ММ.ГГГГ (например: 22.05.2006)'
        }),
        help_text="Вам должно быть не менее 18 лет. Формат: ДД.ММ.ГГГГ"
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        import re
        if not re.match(r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$', phone):
            raise forms.ValidationError("Номер телефона должен быть в формате: '+375 (29) XXX-XX-XX'")
        return phone
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        from datetime import date
        
        age_years = (date.today() - birth_date).days // 365
        if age_years < 18:
            raise forms.ValidationError("Вам должно быть не менее 18 лет")
        if age_years > 100:
            raise forms.ValidationError("Пожалуйста, проверьте правильность введенной даты")
            
        return birth_date
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            Client.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address'],
                birth_date=self.cleaned_data['birth_date']
            )
        return user

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'service_type', 'is_active']

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной")
        return price

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'device_type', 'model', 'serial_number']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['service', 'device', 'parts', 'quantity']

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError("Количество должно быть не менее 1")
        return quantity

class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['service', 'device', 'quantity']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'device': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            })
        }

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Поиск...',
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Все категории"
    )
    price_min = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Мин. цена'})
    )
    price_max = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Макс. цена'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import ServiceType
        self.fields['category'].queryset = ServiceType.objects.all()

class PassportDataForm(forms.ModelForm):
    issue_date = forms.DateField(
        required=True,
        input_formats=['%d.%m.%Y', '%Y-%m-%d'],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ДД.ММ.ГГГГ (например: 15.03.2015)'
        }),
        help_text="Дата выдачи паспорта. Формат: ДД.ММ.ГГГГ"
    )
    
    class Meta:
        model = PassportData
        fields = ['series', 'number', 'issued_by', 'issue_date']

class QuickClientProfileForm(forms.ModelForm):
    """Быстрая форма создания профиля клиента для авторизованных пользователей"""
    birth_date = forms.DateField(
        required=True,
        input_formats=['%d.%m.%Y', '%Y-%m-%d'],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ДД.ММ.ГГГГ (например: 22.05.2006)'
        }),
        help_text="Вам должно быть не менее 18 лет. Формат: ДД.ММ.ГГГГ"
    )
    
    class Meta:
        model = Client
        fields = ['phone', 'address', 'birth_date']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+375 (29) XXX-XX-XX',
                'pattern': r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Введите ваш адрес'
            }),
            'birth_date': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ДД.ММ.ГГГГ (например: 22.05.2006)'
            }),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        import re
        if not re.match(r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$', phone):
            raise forms.ValidationError("Номер телефона должен быть в формате: '+375 (29) XXX-XX-XX'")
        return phone
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        from datetime import date
        
        # Проверяем возраст
        age_years = (date.today() - birth_date).days // 365
        if age_years < 18:
            raise forms.ValidationError("Вам должно быть не менее 18 лет")
        if age_years > 100:
            raise forms.ValidationError("Пожалуйста, проверьте правильность введенной даты")
            
        return birth_date

# Псевдоним для совместимости
ClientProfileForm = QuickClientProfileForm

class UserProfileUpdateForm(forms.ModelForm):
    """Форма для редактирования основной информации пользователя"""
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя пользователя для входа в систему'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваша фамилия'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш email адрес'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)
        
        # Добавляем подсказки
        self.fields['username'].help_text = "Это имя будет использоваться для входа в систему. Может содержать только буквы, цифры и символы @/./+/-/_"
        self.fields['email'].help_text = "На этот адрес будут приходить уведомления"
    
    def clean_username(self):
        username = self.cleaned_data['username']
        
        # Проверяем, что username уникален (исключая текущего пользователя)
        if User.objects.filter(username=username).exclude(id=self.user_id).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует")
        
        # Дополнительная валидация username
        import re
        if not re.match(r'^[\w.@+-]+$', username):
            raise forms.ValidationError("Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_")
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Проверяем, что email уникален (исключая текущего пользователя)
        if User.objects.filter(email=email).exclude(id=self.user_id).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        
        return email


class ClientProfileUpdateForm(forms.ModelForm):
    """Форма для редактирования профиля клиента"""
    
    birth_date = forms.DateField(
        required=False,
        input_formats=['%d.%m.%Y', '%Y-%m-%d'],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ДД.ММ.ГГГГ (например: 15.03.1990)'
        }),
        help_text="Формат: ДД.ММ.ГГГГ"
    )
    
    class Meta:
        model = Client
        fields = ['phone', 'address', 'birth_date']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+375 (29) XXX-XX-XX'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ваш адрес'
            }),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            import re
            if not re.match(r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$', phone):
                raise forms.ValidationError("Номер телефона должен быть в формате: '+375 (29) XXX-XX-XX'")
        return phone
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            from datetime import date
            
            # Проверяем возраст
            age_years = (date.today() - birth_date).days // 365
            if age_years < 18:
                raise forms.ValidationError("Вам должно быть не менее 18 лет")
            if age_years > 100:
                raise forms.ValidationError("Пожалуйста, проверьте правильность введенной даты")
                
        return birth_date
