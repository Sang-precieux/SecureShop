"""Paiements *simulés* uniquement : pas d'opérateur réel, pas de vrai débit."""
import secrets
import uuid
import random
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction as db_transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from shop.models import Product
from .models import SecurityEvent, Transaction
from .security import generate_nonce, sign, verify

SCENARIOS = {
    'success': 'VALIDEE',
    'refused': 'REFUSEE',
    'pending': 'EN_ATTENTE',
}
def simulate_payment():
    """Simule automatiquement le résultat d'un paiement."""
    return random.choices(
        ['VALIDEE', 'REFUSEE', 'EN_ATTENTE'],
        weights=[80, 10, 10],
        k=1
    )[0]


def cart_data(request):
    basket = request.session.get('cart', {})
    ids = [int(k) for k in basket if str(k).isdigit()]
    items = []
    total = Decimal('0.00')
    for product in Product.objects.filter(pk__in=ids):
        try:
            qty = max(0, min(int(basket.get(str(product.pk), 0)), 99))
        except (TypeError, ValueError):
            qty = 0
        if qty:
            subtotal = product.price * qty
            total += subtotal
            items.append((product, qty, subtotal))
    return items, total


@login_required
@require_http_methods(['GET'])
def checkout(request):
    if request.user.is_staff:
        raise PermissionDenied('Utilisez un compte client pour réaliser des achats.')
    items, total = cart_data(request)
    if not items:
        return redirect('products')
    token = request.session.get('checkout_token')
    if not token:
        token = uuid.uuid4().hex
        request.session['checkout_token'] = token
    return render(request, 'payments/checkout.html', {
        'items': items, 'total': total, 'checkout_token': token,
        'payment_methods': Transaction.METHOD_CHOICES,
    })


def _payment_result(request, tx):
    template = {
        'VALIDEE': 'payments/success.html',
        'REFUSEE': 'payments/failed.html',
        'EN_ATTENTE': 'payments/pending.html',
    }[tx.status]
    return render(request, template, {'tx': tx, 'receipt_items': tx.cart_snapshot})


@login_required
@require_http_methods(['POST'])
def process(request):
    if request.user.is_staff:
        raise PermissionDenied('Paiement réservé aux clients.')
    method = request.POST.get('payment_method')
    scenario = None
    if method not in dict(Transaction.METHOD_CHOICES):
     return HttpResponseBadRequest('Mode ou scénario de simulation invalide.')

                # Vérification du numéro Mobile Money
    if method in ['MPESA', 'ORANGE', 'AIRTEL']:
        phone = request.POST.get('phone', '').strip()

        if phone.startswith('+243'):
            valid_phone = (
                len(phone) == 13
                and phone[4:].isascii()
                and phone[4:].isdigit()
                and phone[4] in ('8', '9')
            )

            if valid_phone:
                phone = '0' + phone[4:]

        else:
            valid_phone = (
                len(phone) == 10
                and phone.isascii()
                and phone.isdigit()
                and phone.startswith(('08', '09'))
            )

        if not valid_phone:
            return HttpResponseBadRequest(
                "Numéro Mobile Money invalide. "
                "Saisissez 10 chiffres commençant par 08 ou 09, "
                "ou +243 suivi de 9 chiffres sans zéro."
            )
        
    token = request.POST.get('checkout_token', '')
    expected = request.session.get('checkout_token', '')
    if not token or not expected or not secrets.compare_digest(token, expected):
        previous = Transaction.objects.filter(user=request.user, idempotency_key=token).first() if token else None
        if previous:
            return _payment_result(request, previous)
        return HttpResponseBadRequest('Session de paiement expirée. Rechargez le panier.')

    items, total = cart_data(request)  # Toujours recalculer les prix côté serveur
    if not items or total <= 0:
        return redirect('products')

    ref = 'PAY-' + uuid.uuid4().hex[:20].upper()
    nonce = generate_nonce()
    hmac_value = sign(ref, str(total), nonce)
    valid_signature = verify(ref, str(total), nonce, hmac_value)
    if not valid_signature:
        return HttpResponseBadRequest('Échec du contrôle d’intégrité.')

    status = simulate_payment()
    snapshot = [
        {'product_id': p.pk, 'name': p.name, 'unit_price': str(p.price),
         'quantity': qty, 'subtotal': str(sub)}
        for p, qty, sub in items
    ]
    try:
        with db_transaction.atomic():
            tx = Transaction.objects.create(
                user=request.user, reference=ref, amount=total, nonce=nonce,
                hmac_signature=hmac_value, payment_method=method, status=status,
                cart_snapshot=snapshot, idempotency_key=token,
            )
            SecurityEvent.objects.create(
                test_type='normal', user=request.user, transaction=tx,
                original_amount=total, received_amount=total, nonce=nonce,
                received_hmac=hmac_value, calculated_hmac=hmac_value,
                hmac_valid=True, nonce_valid=True,
                accepted=(status == 'VALIDEE'),
                reason=f"Paiement fictif : statut {status}. Aucun débit réel.",
            )
    except IntegrityError:
        # Requête identique déjà enregistrée : ne surtout pas créer un second paiement
        previous = Transaction.objects.filter(user=request.user, idempotency_key=token).first()
        if previous:
            return _payment_result(request, previous)
        raise

    request.session.pop('checkout_token', None)
    if status == 'VALIDEE':
        request.session['cart'] = {}
    return _payment_result(request, tx)
