from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import RedirectView
from shop.views import home

urlpatterns = [
    # L'admin natif Django est volontairement désactivé : il contournerait l'OTP personnalisé.
    path('admin/', RedirectView.as_view(pattern_name='admin_login', permanent=False)),
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('', include('shop.urls')),
    path('paiement/', include('payments.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
