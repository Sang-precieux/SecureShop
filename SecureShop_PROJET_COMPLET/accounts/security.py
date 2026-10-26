from functools import wraps
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.urls import reverse


def admin_otp_required(view):
    """Bloque TOUT accès admin si OTP admin non validé dans cette session."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse('admin_login'))
        if not request.user.is_active or not request.user.is_staff or not request.session.get('admin_otp_verified', False):
            raise PermissionDenied('Accès réservé aux administrateurs vérifiés par OTP.')
        return view(request, *args, **kwargs)
    return wrapped
