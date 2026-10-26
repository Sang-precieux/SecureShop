from decimal import Decimal
from django.core.management.base import BaseCommand
from shop.models import Product

DEMO_PRODUCTS = [
    ('Ordinateur portable', 'Dell Inspiron 15', '500.00', 'laptop'),
    ('Smartphone', 'Samsung Galaxy', '300.00', 'mobile-screen-button'),
    ('Casque audio', 'Casque stéréo', '50.00', 'headphones'),
    ('Souris sans fil', 'Souris Bluetooth', '20.00', 'computer-mouse'),
    ('Clavier', 'Clavier mécanique', '45.00', 'keyboard'),
    ('Disque SSD', 'SSD portable', '95.00', 'hard-drive'),
]

class Command(BaseCommand):
    help = 'Crée les produits exemples si absents (sans modifier les produits existants).'

    def handle(self, *args, **options):
        added = 0
        for name, description, price, icon in DEMO_PRODUCTS:
            _, created = Product.objects.get_or_create(
                name=name,
                defaults={'description': description, 'price': Decimal(price), 'icon': icon},
            )
            added += int(created)
        self.stdout.write(self.style.SUCCESS(f'{added} produit(s) de démonstration ajouté(s).'))
