"""HMAC de démonstration. Ne constitue pas une passerelle de paiement réelle."""
import hashlib
import hmac
import json
import os
import secrets

from django.core.exceptions import ImproperlyConfigured

def _key():
    value = os.getenv('PAYMENT_HMAC_KEY', '')
    if len(value) < 32:
        raise ImproperlyConfigured('Clé HMAC absente : relancez INSTALLER_WINDOWS.bat.')
    return value.encode('utf-8')

def generate_nonce():
    return secrets.token_hex(24)

def sign(reference, amount, nonce):
    payload = json.dumps([str(reference), str(amount), str(nonce)], separators=(',', ':'), ensure_ascii=False)
    return hmac.new(_key(), payload.encode('utf-8'), hashlib.sha256).hexdigest()

def verify(reference, amount, nonce, signature):
    return hmac.compare_digest(sign(reference, amount, nonce), str(signature))
