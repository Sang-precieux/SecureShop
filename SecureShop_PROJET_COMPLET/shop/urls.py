from django.urls import path
from . import views

urlpatterns = [
    path('produits/', views.products, name='products'),
    path('panier/', views.cart, name='cart'),
    path('panier/ajouter/<int:pk>/', views.add_cart, name='add_cart'),
    path('panier/modifier/<int:pk>/', views.update_cart, name='update_cart'),
    path('panier/vider/', views.clear_cart, name='clear_cart'),
]
