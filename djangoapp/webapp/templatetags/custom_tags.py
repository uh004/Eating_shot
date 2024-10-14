from django import template

register = template.Library()


@register.filter
def length(value):
    return len(value)


@register.filter
def split_by_comma(value):
    return value.split(",")


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def subtract(value, arg):
    return value - arg
