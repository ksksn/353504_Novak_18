from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Repair, Contract, Order, Service, SparePart, Part

class ServiceChoiceField(forms.ModelChoiceField):
    """Кастомное поле выбора услуги с отображением цены"""
    
    def label_from_instance(self, obj):
        return f"{obj.name} - {obj.price:.2f} руб."

class SparePartChoiceField(forms.ModelChoiceField):
    """Кастомное поле выбора запчасти с отображением цены"""
    
    def label_from_instance(self, obj):
        return f"{obj.name} - {obj.price:.2f} руб. (в наличии: {obj.quantity_in_stock})"

class PartChoiceField(forms.ModelMultipleChoiceField):
    """Кастомное поле выбора деталей с отображением цены"""
    
    def label_from_instance(self, obj):
        return f"{obj.name} - {obj.price:.2f} руб."

class RepairAdminForm(forms.ModelForm):
    """Кастомная форма для ремонта с автоматическим расчетом"""
    
    class Meta:
        model = Repair
        fields = '__all__'
        widgets = {
            'total_cost': forms.NumberInput(attrs={
                'readonly': True,
                'class': 'readonly-total',
                'style': 'background-color: #f8f9fa; font-weight: bold; color: #198754;'
            }),
            'labor_cost': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'onchange': 'calculateRepairTotal()',
                'placeholder': 'Введите стоимость работ'
            })
        }

class OrderAdminForm(forms.ModelForm):
    """Кастомная форма для заказа с автоматическим расчетом"""
    
    service = ServiceChoiceField(
        queryset=Service.objects.filter(is_active=True),
        empty_label="Выберите услугу",
        widget=forms.Select(attrs={
            'onchange': 'calculateOrderTotal()',
            'data-price-attr': 'true'
        })
    )
    
    parts = PartChoiceField(
        queryset=Part.objects.filter(in_stock=True),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple('Детали', False, attrs={
            'onchange': 'calculateOrderTotal()'
        })
    )
    
    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'min': '1',
                'onchange': 'calculateOrderTotal()',
                'placeholder': 'Количество'
            }),
            'service_sum': forms.NumberInput(attrs={
                'readonly': True,
                'class': 'readonly-total'
            }),
            'parts_sum': forms.NumberInput(attrs={
                'readonly': True,
                'class': 'readonly-total'
            }),
            'total_sum': forms.NumberInput(attrs={
                'readonly': True,
                'class': 'readonly-total',
                'style': 'background-color: #f8f9fa; font-weight: bold; color: #198754;'
            })
        }

class ContractAdminForm(forms.ModelForm):
    """Кастомная форма для договора с автоматическим расчетом"""
    
    class Meta:
        model = Contract
        fields = '__all__'
        widgets = {
            'total_sum': forms.NumberInput(attrs={
                'readonly': True,
                'class': 'readonly-total',
                'style': 'background-color: #f8f9fa; font-weight: bold; color: #198754;'
            }),
            'number': forms.TextInput(attrs={
                'placeholder': 'Например: DOG-2024-001'
            }),
            'date_signed': forms.DateInput(attrs={
                'type': 'date'
            }),
            'deadline': forms.DateInput(attrs={
                'type': 'date'
            })
        }

class RepairSparePartInlineForm(forms.ModelForm):
    """Форма для inline запчастей в ремонте"""
    
    spare_part = SparePartChoiceField(
        queryset=SparePart.objects.filter(quantity_in_stock__gt=0),
        widget=forms.Select(attrs={
            'onchange': 'calculateRepairTotal()',
            'data-price-attr': 'true'
        })
    )
    
    class Meta:
        model = Repair.spare_parts.through
        fields = '__all__'
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'min': '1',
                'onchange': 'calculateRepairTotal()',
                'placeholder': 'Кол-во'
            })
        }
