from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

class AccesAdminTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user('client@example.com', 'client@example.com', 'pass1234Test!')
        self.admin = User.objects.create_superuser('admin@example.com', 'admin@example.com', 'pass1234Test!')

    def test_client_ne_voit_pas_journal(self):
        self.client.force_login(self.customer)
        self.assertEqual(self.client.get(reverse('payment_journal')).status_code, 403)

    def test_admin_doit_valider_otp(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('admin_dashboard')).status_code, 403)
        self.client.session['admin_otp_verified'] = True
        self.client.session.save()
        self.assertEqual(self.client.get(reverse('admin_dashboard')).status_code, 403)
        # Django test Client conserve une nouvelle session via property : forcer explicitement
        session = self.client.session
        session['admin_otp_verified'] = True
        session.save()
        self.assertEqual(self.client.get(reverse('admin_dashboard')).status_code, 200)
