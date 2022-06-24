""" В template.Library зарегистрированы все встроенные теги и фильтры шаблонов;
добавляем к ним и наш фильтр.
синтаксис @register... , под который описана функция addclass() -
# это применение "декораторов", функций, меняющих поведение функций
"""
from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})
