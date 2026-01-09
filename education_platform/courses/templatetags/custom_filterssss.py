from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Получение элемента из словаря по ключу в шаблоне"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def debug(obj):
    """Выводит тип и значение объекта (для отладки)"""
    return f"Type: {type(obj)}, Value: {obj}"