from django import template

register = template.Library()


@register.filter
def length(value):
    return len(value)


@register.filter
def split_by_comma(value):
    return value.split(",")
