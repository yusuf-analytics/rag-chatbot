from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    GENDER_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Unisex', 'Unisex'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Unisex')

    CATEGORY_CHOICES = [
        ('Sweater', 'Sweater'),
        ('Cardigan', 'Cardigan'),
        ('Inner', 'Inner'),
        ('Polo', 'Polo'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Sweater')

    # Attributes
    material = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True, help_text="e.g. S, M, L, XL")
    color = models.CharField(max_length=100, blank=True, help_text="e.g. Red, Blue")
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class SiteConfig(models.Model):
    THEME_CHOICES = [
        ('default', 'Default (Clean/Editorial)'),
    ]
    active_theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='default')

    def __str__(self):
        return "Site Configuration"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

    @property
    def is_default(self):
        return self.active_theme == 'default'
