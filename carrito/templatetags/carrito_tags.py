from django import template

register = template.Library()

@register.filter
def total_unidades(carrito):
    return sum(item['cantidad'] for item in carrito.values())
