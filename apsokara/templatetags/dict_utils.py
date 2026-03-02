from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template mein dynamic dictionary key access karne ke liye: {{ dict|get_item:key }}"""
    if dictionary:
        return dictionary.get(key)
    return None
