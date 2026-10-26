from decimal import Decimal

from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Product

MAX_QUANTITY = 99


def home(request):
    return render(request, 'shop/home.html', {
        'featured_products': Product.objects.all()[:3],
    })


def products(request):
    return render(request, 'shop/products.html', {
        'products': Product.objects.all().order_by('id'),
    })


@require_POST
def add_cart(request, pk):
    get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})
    key = str(pk)
    try:
        current = max(0, int(cart.get(key, 0)))
    except (TypeError, ValueError):
        current = 0
    cart[key] = min(current + 1, MAX_QUANTITY)
    request.session['cart'] = cart
    messages.success(request, 'Produit ajouté au panier !')
    return redirect('products')


def cart(request):
    basket = request.session.get('cart', {})
    ids = [int(k) for k in basket if str(k).isdigit()]
    items = []
    total = Decimal('0.00')
    total_articles = 0
    for product in Product.objects.filter(pk__in=ids):
        try:
            qty = max(0, min(int(basket.get(str(product.pk), 0)), MAX_QUANTITY))
        except (TypeError, ValueError):
            qty = 0
        if not qty:
            continue
        subtotal = product.price * qty
        total += subtotal
        total_articles += qty
        items.append((product, qty, subtotal))
    return render(request, 'shop/cart.html', {
        'items': items, 'total': total, 'total_articles': total_articles,
    })


@require_POST
def clear_cart(request):
    request.session['cart'] = {}
    messages.info(request, 'Le panier a été vidé.')
    return redirect('cart')


@require_POST
def update_cart(request, pk):
    get_object_or_404(Product, pk=pk)
    action = request.POST.get('action')
    if action not in ('increment', 'decrement', 'remove'):
        return HttpResponseBadRequest('Action invalide')
    basket = request.session.get('cart', {})
    key = str(pk)
    try:
        qty = max(0, min(int(basket.get(key, 0)), MAX_QUANTITY))
    except (TypeError, ValueError):
        qty = 0
    if action == 'increment':
        basket[key] = min(qty + 1, MAX_QUANTITY)
    elif action == 'decrement':
        if qty > 1:
            basket[key] = qty - 1
        else:
            basket.pop(key, None)
    else:
        basket.pop(key, None)
    request.session['cart'] = basket
    return redirect('cart')
