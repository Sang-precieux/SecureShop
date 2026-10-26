from django.conf import settings
from django.db import models


class Transaction(models.Model):
    METHOD_CHOICES = [
     ('MPESA', 'M-Pesa'),
    ('ORANGE', 'Orange Money'),
    ('AIRTEL', 'Airtel Money'),
    ('VISA', 'Carte Visa'),
    ('MASTERCARD', 'Carte Mastercard'),
    ('CARD', 'Autre carte bancaire (simulation)'),
    ]
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDEE', 'Validée'),
        ('REFUSEE', 'Refusée'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reference = models.CharField(max_length=40, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    nonce = models.CharField(max_length=64, unique=True)
    hmac_signature = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EN_ATTENTE')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='CARD')
    # Reçu: prix/noms/quantités figés à la date de la commande
    cart_snapshot = models.JSONField(default=list, blank=True)
    # Un clic redoublé ne doit pas créer deux transactions
    idempotency_key = models.CharField(max_length=64, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference


class SecurityEvent(models.Model):
    TEST_TYPES = [
        ('normal', 'Transaction normale'),
        ('tamper_amount', 'Altération du montant'),
        ('replay', 'Attaque par rejeu'),
        ('fake_hmac', 'Falsification HMAC'),
        ('manual_tamper', 'Manipulation manuelle'),
        ('manual_replay', 'Rejeu manuel'),
    ]
    test_type = models.CharField(max_length=30, choices=TEST_TYPES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True, related_name='security_events')
    original_amount = models.DecimalField(max_digits=12, decimal_places=2)
    received_amount = models.DecimalField(max_digits=12, decimal_places=2)
    nonce = models.CharField(max_length=128)
    received_hmac = models.CharField(max_length=128)
    calculated_hmac = models.CharField(max_length=128)
    hmac_valid = models.BooleanField(default=False)
    nonce_valid = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_test_type_display()} - {'Accepté' if self.accepted else 'Refusé'}"
