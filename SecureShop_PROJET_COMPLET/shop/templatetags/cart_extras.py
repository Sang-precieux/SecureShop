from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def cart_total(context):
    """Quantités totales du panier pour le badge du menu."""
    request = context.get('request')
    if not request:
        return 0
    basket = request.session.get('cart', {})
    count = 0
    for value in basket.values():
        try:
            count += max(0, min(int(value), 99))
        except (TypeError, ValueError):
            continue
    return count
