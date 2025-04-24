from django import template

register = template.Library()

@register.filter
def get_order_items(order_items, order_id):
    return [item for item in order_items if item['order_id'] == order_id]