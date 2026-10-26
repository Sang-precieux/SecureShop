from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from .models import Product

class PanierTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test', price=Decimal('10.00'), icon='box')

    def test_ajout_et_increment_puis_suppression(self):
        add_url = reverse('add_cart', args=(self.product.pk,))
        update_url = reverse('update_cart', args=(self.product.pk,))
        self.assertEqual(self.client.get(add_url).status_code, 405)
        self.client.post(add_url)
        self.client.post(add_url)
        self.assertContains(self.client.get(reverse('cart')), '2')
        self.client.post(update_url, {'action': 'decrement'})
        self.assertEqual(self.client.session['cart'][str(self.product.pk)], 1)
        self.client.post(update_url, {'action': 'remove'})
        self.assertFalse(self.client.session['cart'])
