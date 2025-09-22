from django import template
from django.db.models import Sum

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sum_attr(value, arg):
    """Sum the values of a given attribute on a queryset"""
    try:
        return sum(float(getattr(obj, arg) or 0) for obj in value)
    except (ValueError, TypeError, AttributeError):
        return 0

@register.filter
def sub(value, arg):
    """Subtract arg from value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divisibleby(value, arg):
    """Divide value by arg"""
    try:
        arg = float(arg)
        if arg != 0:
            return float(value) / arg
        else:
            return 0
    except (ValueError, TypeError):
        return 0 