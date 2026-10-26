from django.urls import path
from .views import (
    register, otp_login, admin_login, verify_otp, secure_logout,
    admin_dashboard, admin_users, admin_products,
    admin_product_create, admin_product_edit, admin_product_delete,admin_user_toggle
)

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', otp_login, name='login'),
    path('admin-login/', admin_login, name='admin_login'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('logout/', secure_logout, name='logout'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-users/', admin_users, name='admin_users'),
    path('admin-products/', admin_products, name='admin_products'),
    path('admin-products/create/', admin_product_create, name='admin_product_create'),
    path('admin-products/<int:pk>/edit/', admin_product_edit, name='admin_product_edit'),
    path('admin-products/<int:pk>/delete/', admin_product_delete, name='admin_product_delete'),
    path(
    'admin-users/<int:pk>/toggle/',
    admin_user_toggle,
    name='admin_user_toggle'
),
]
