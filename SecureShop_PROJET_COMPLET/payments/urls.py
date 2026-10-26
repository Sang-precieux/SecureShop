from django.urls import path
from . import views
from .lab import payment_journal, integrity_lab, security_journal

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('traiter/', views.process, name='process_payment'),
    path('journal/', payment_journal, name='payment_journal'),
    path('journal-securite/', security_journal, name='security_journal'),
    path('tester/<int:tx_id>/', integrity_lab, name='integrity_lab'),
]
