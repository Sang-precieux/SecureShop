"""Journal et démonstration HMAC accessibles uniquement après OTP admin."""
import hmac
from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from accounts.security import admin_otp_required
from .models import SecurityEvent, Transaction
from .security import sign


@never_cache
@admin_otp_required
def payment_journal(request):
    transactions = Transaction.objects.select_related('user').order_by('-created_at')
    return render(request, 'payments/payment_journal.html', {'transactions': transactions})


@never_cache
@admin_otp_required
@require_http_methods(['GET', 'POST'])
def integrity_lab(request, tx_id):
    tx = get_object_or_404(Transaction, pk=tx_id)
    result = None
    form_data = {
        'reference': tx.reference, 'amount': str(tx.amount),
        'nonce': tx.nonce, 'signature': tx.hmac_signature,
    }
    if request.method == 'POST':
        form_data = {
            'reference': request.POST.get('reference', '').strip(),
            'amount': request.POST.get('amount', '').strip(),
            'nonce': request.POST.get('nonce', '').strip(),
            'signature': request.POST.get('signature', '').strip(),
        }
        try:
            amount = Decimal(form_data['amount'])
            if not amount.is_finite():
                raise InvalidOperation
            calculated = sign(form_data['reference'], str(amount), form_data['nonce'])
            hmac_valid = hmac.compare_digest(form_data['signature'], calculated)
            nonce_owner = Transaction.objects.filter(nonce=form_data['nonce']).first()
            nonce_valid = bool(nonce_owner and nonce_owner.pk == tx.pk)
            same_reference = form_data['reference'] == tx.reference
            same_amount = amount == tx.amount
            exact_original = all((hmac_valid, nonce_valid, same_reference, same_amount))
            if not hmac_valid:
                reason = 'Signature HMAC incohérente : message altéré ou signature falsifiée.'
                event_type = 'manual_tamper'
            elif not nonce_valid:
                reason = 'Nonce non reconnu pour cette transaction (scénario anti-rejeu).'
                event_type = 'manual_replay'
            elif exact_original:
                reason = 'Simulation d’un second envoi identique : considéré comme rejeu dans ce laboratoire.'
                event_type = 'manual_replay'
            else:
                reason = 'Données différentes de la transaction initiale.'
                event_type = 'manual_tamper'
            SecurityEvent.objects.create(
                test_type=event_type, user=request.user, transaction=tx,
                original_amount=tx.amount, received_amount=amount,
                nonce=form_data['nonce'], received_hmac=form_data['signature'],
                calculated_hmac=calculated, hmac_valid=hmac_valid,
                nonce_valid=nonce_valid and not exact_original,
                accepted=False, reason=reason,
            )
            result = {
                'accepted': False, 'reason': reason, 'calculated_hmac': calculated,
                'hmac_valid': hmac_valid, 'nonce_valid': nonce_valid and not exact_original,
                'replay': exact_original, 'https_active': request.is_secure(),
            }
        except (InvalidOperation, ValueError, OverflowError):
            result = {'accepted': False, 'reason': 'Montant invalide.', 'hmac_valid': False,
                      'nonce_valid': False, 'https_active': request.is_secure()}
    security_events = SecurityEvent.objects.filter(transaction=tx).order_by('-created_at')[:20]
    return render(request, 'payments/integrity_lab.html', {
        'tx': tx, 'form_data': form_data,
        'result': result, 'security_events': security_events,
    })


@never_cache
@admin_otp_required
def security_journal(request):
    events = SecurityEvent.objects.select_related('user', 'transaction').order_by('-created_at')[:500]
    return render(request, 'payments/security_journal.html', {'events': events})
