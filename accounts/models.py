from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with a role field to distinguish farmers,
    buyers, dispatchers, and admins.
    """

    class Role(models.TextChoices):
        FARMER = 'farmer', 'Farmer'
        BUYER = 'buyer', 'Buyer'
        DISPATCHER = 'dispatcher', 'Dispatcher'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.FARMER,
    )
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.username} ({self.role})'

    @property
    def is_farmer(self):
        return self.role == self.Role.FARMER

    @property
    def is_buyer(self):
        return self.role == self.Role.BUYER

    @property
    def is_dispatcher(self):
        return self.role == self.Role.DISPATCHER


class FarmerProfile(models.Model):
    """Extended profile for farmers."""

    class Language(models.TextChoices):
        HAUSA = 'ha', 'Hausa'
        YORUBA = 'yo', 'Yoruba'
        IGBO = 'ig', 'Igbo'
        PIDGIN = 'pcm', 'Nigerian Pidgin'
        ENGLISH = 'en', 'English'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='farmer_profile',
    )
    state = models.CharField(max_length=100, blank=True)
    lga = models.CharField(max_length=100, blank=True, verbose_name='LGA')
    preferred_language = models.CharField(
        max_length=5,
        choices=Language.choices,
        default=Language.ENGLISH,
    )
    farm_size_hectares = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Profile: {self.user.username}'


class BuyerProfile(models.Model):
    """Extended profile for buyers."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='buyer_profile',
    )
    business_name = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    verified_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Buyer Profile: {self.user.username}'
