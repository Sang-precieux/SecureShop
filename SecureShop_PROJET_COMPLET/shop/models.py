from django.db import models

class Product(models.Model):
    name = models.CharField('Nom', max_length=120, unique=True)
    description = models.TextField('Description', blank=True)
    price = models.DecimalField('Prix en USD', max_digits=10, decimal_places=2)
    icon = models.CharField('Icône Font Awesome', max_length=60, default='box')
    image = models.ImageField(
    upload_to='products/',
    blank=True,
    null=True
)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name
