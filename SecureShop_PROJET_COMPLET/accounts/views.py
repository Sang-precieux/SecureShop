import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Sum
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from payments.models import SecurityEvent, Transaction
from shop.models import Product
from .forms import RegistrationForm, EmailAuthenticationForm
from .models import LoginOTP
from .security import admin_otp_required

OTP_LIFETIME_SECONDS = 40
OTP_MAX_ATTEMPTS = 3


def otp_hash(user_id, code):
    return salted_hmac('secureshop.login.otp', f'{user_id}:{code}').hexdigest()


def start_otp(request, user, purpose):
    """Envoi avant login(); préserve uniquement le panier client, pas les sessions d'auth."""
    if purpose not in ('login', 'register', 'admin_login'):
        return False
    code = f'{secrets.randbelow(1000000):06d}'
    expires = timezone.now() + timedelta(seconds=OTP_LIFETIME_SECONDS)
    basket = request.session.get('cart', {}) if purpose != 'admin_login' else {}
    request.session.flush()
    if basket and isinstance(basket, dict):
        request.session['cart'] = basket
    LoginOTP.objects.update_or_create(
        user=user,
        defaults={'code_hash': otp_hash(user.pk, code), 'expires_at': expires,
                  'attempts': 0, 'used': False},
    )
    request.session['otp_pending_user'] = user.pk
    request.session['otp_purpose'] = purpose
    try:
        send_mail(
            'SecureShop - Code OTP',
            f'Votre code OTP SecureShop : {code}\nValable 40 secondes. Ne le partagez jamais.',
            settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False,
        )
    except Exception:
        LoginOTP.objects.filter(user=user).delete()
        request.session.flush()
        return False
    return True


@never_cache
@require_http_methods(['GET', 'POST'])
def register(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff and request.session.get('admin_otp_verified') else 'products')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.is_staff = False  # Inscription publique = jamais administrateur
        user.is_superuser = False
        user.save()
        if start_otp(request, user, 'register'):
            return redirect('verify_otp')
        user.delete()
        messages.error(request, "Échec d'envoi de l'OTP. Vérifiez la configuration e-mail.")
        return redirect('register')
    return render(request, 'registration/register.html', {'form': form})


@never_cache
@require_http_methods(['GET', 'POST'])
def otp_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard' if request.session.get('admin_otp_verified') else 'admin_login')
        return redirect('products')
    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if user.is_staff:
            messages.error(request, "Compte administrateur : utilisez l'accès administrateur.")
            return redirect('admin_login')
        if start_otp(request, user, 'login'):
            return redirect('verify_otp')
        messages.error(request, "Impossible d'envoyer le code OTP.")
    return render(request, 'registration/login.html', {'form': form})


@never_cache
@require_http_methods(['GET', 'POST'])
def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff and request.session.get('admin_otp_verified'):
            return redirect('admin_dashboard')
        # Une session existante non vérifiée ne doit pas servir à contourner l'OTP.
        logout(request)
    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if not user.is_staff or not user.is_active:
            messages.error(request, 'Accès administrateur non autorisé.')
        elif start_otp(request, user, 'admin_login'):
            return redirect('verify_otp')
        else:
            messages.error(request, "Impossible d'envoyer le code OTP.")
    return render(request, 'registration/admin_login.html', {'form': form})


@never_cache
@require_http_methods(['GET', 'POST'])
def verify_otp(request):
    user_id = request.session.get('otp_pending_user')
    purpose = request.session.get('otp_purpose')
    if not user_id or purpose not in ('login', 'register', 'admin_login'):
        return redirect('login')
    retry_route = 'register' if purpose == 'register' else ('admin_login' if purpose == 'admin_login' else 'login')
    challenge = LoginOTP.objects.filter(user_id=user_id).first()
    if (not challenge or challenge.used or challenge.expires_at <= timezone.now()
            or challenge.attempts >= OTP_MAX_ATTEMPTS):
        LoginOTP.objects.filter(user_id=user_id).delete()
        request.session.flush()
        messages.error(request, 'OTP expiré ou invalide. Recommencez.')
        return redirect(retry_route)
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        accepted = False
        if len(code) == 6 and code.isascii() and code.isdigit():
            with transaction.atomic():
                current = LoginOTP.objects.select_for_update().filter(user_id=user_id).first()
                if (current and not current.used and current.expires_at > timezone.now()
                        and current.attempts < OTP_MAX_ATTEMPTS):
                    current.attempts += 1
                    if constant_time_compare(current.code_hash, otp_hash(user_id, code)):
                        current.used = True
                        accepted = True
                    current.save(update_fields=['attempts', 'used'])
        if accepted:
            user = User.objects.filter(pk=user_id).first()
            if not user or (purpose == 'admin_login' and not (user.is_active and user.is_staff)) or (purpose == 'login' and (not user.is_active or user.is_staff)):
                LoginOTP.objects.filter(user_id=user_id).delete()
                request.session.flush()
                messages.error(request, 'Compte non autorisé pour cette connexion.')
                return redirect(retry_route)
            if purpose == 'register':
                user.is_active = True
                user.save(update_fields=['is_active'])
            request.session.pop('otp_pending_user', None)
            request.session.pop('otp_purpose', None)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # Le drapeau admin n'est posé QU'APRÈS la vérification du code.
            request.session['admin_otp_verified'] = (purpose == 'admin_login')
            LoginOTP.objects.filter(user=user).delete()
            messages.success(request, 'Authentification réussie !')
            return redirect('admin_dashboard' if purpose == 'admin_login' else 'products')
        challenge = LoginOTP.objects.filter(user_id=user_id).first()
        if not challenge or challenge.expires_at <= timezone.now() or challenge.attempts >= OTP_MAX_ATTEMPTS:
            LoginOTP.objects.filter(user_id=user_id).delete()
            request.session.flush()
            messages.error(request, 'OTP expiré ou nombre de tentatives dépassé.')
            return redirect(retry_route)
        messages.error(request, 'Code OTP invalide.')
    seconds = max(0, int((challenge.expires_at - timezone.now()).total_seconds() + 0.999))
    return render(request, 'registration/verify_otp.html', {'seconds': seconds})


@require_POST
def secure_logout(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('home')


@never_cache
@admin_otp_required
def admin_dashboard(request):
    paid = Transaction.objects.filter(status='VALIDEE')
    stats = {
        'users': User.objects.filter(is_staff=False).count(),
        'products': Product.objects.count(),
        'payments': Transaction.objects.count(),
        'validated': paid.count(),
        'refused': Transaction.objects.filter(status='REFUSEE').count(),
        'pending': Transaction.objects.filter(status='EN_ATTENTE').count(),
        'revenue': paid.aggregate(total=Sum('amount'))['total'] or 0,
        'security_events': SecurityEvent.objects.count(),
    }
    recent = Transaction.objects.select_related('user').order_by('-created_at')[:8]
    return render(request, 'administration/dashboard.html', {'stats': stats, 'recent': recent})


@admin_otp_required
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')[:200]
    return render(request, 'administration/users.html', {'users': users})
@admin_otp_required
@require_POST
def admin_user_toggle(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_staff or user.is_superuser:
        raise PermissionDenied(
            "Les administrateurs sont gérés uniquement via le terminal."
        )

    if user.pk == request.user.pk:
        messages.error(
            request,
            "Vous ne pouvez pas désactiver votre propre compte."
        )
        return redirect('admin_users')

    if user.is_superuser and not request.user.is_superuser:
        raise PermissionDenied

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])

    messages.success(
        request,
        "Statut du compte modifié avec succès."
    )
    return redirect('admin_users')


@admin_otp_required
@require_POST
def admin_user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)

    if user.pk == request.user.pk:
        messages.error(
            request,
            "Vous ne pouvez pas supprimer votre propre compte."
        )
        return redirect('admin_users')

    # Seul un superutilisateur peut supprimer un administrateur.
    if user.is_staff and not request.user.is_superuser:
        raise PermissionDenied

    # Protection des superutilisateurs.
    if user.is_superuser:
        messages.error(
            request,
            "La suppression d'un superutilisateur est interdite depuis cette interface."
        )
        return redirect('admin_users')

    # Éviter la suppression des données liées aux commandes et paiements.
    if Transaction.objects.filter(user=user).exists():
        messages.error(
            request,
            "Ce compte possède des transactions. Désactivez-le plutôt."
        )
        return redirect('admin_users')

    user.delete()

    messages.success(
        request,
        "Compte utilisateur supprimé avec succès."
    )
    return redirect('admin_users')

    users = User.objects.all().order_by('-date_joined')[:200]
    return render(request, 'administration/users.html', {'users': users})


def _product_form_class():
    fields = [f.name for f in Product._meta.fields if f.editable]
    allowed = [name for name in ('name', 'description', 'price', 'icon', 'image') if name in fields]
    return modelform_factory(Product, fields=allowed)


@admin_otp_required
def admin_products(request):
    return render(request, 'administration/products.html', {
        'products': Product.objects.all().order_by('-id'),
    })


@admin_otp_required
@require_http_methods(['GET', 'POST'])
def admin_product_create(request):
    Form = _product_form_class()
    form = Form(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Produit ajouté.')
        return redirect('admin_products')
    return render(request, 'administration/product_form.html', {'form': form, 'heading': 'Ajouter un produit'})


@admin_otp_required
@require_http_methods(['GET', 'POST'])
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Form = _product_form_class()
    form = Form(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Produit modifié.')
        return redirect('admin_products')
    return render(request, 'administration/product_form.html', {'form': form, 'heading': f'Modifier : {product.name}'})


@admin_otp_required
@require_http_methods(['GET', 'POST'])
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Produit supprimé.')
        return redirect('admin_products')
    return render(request, 'administration/product_delete.html', {'product': product})
