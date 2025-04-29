from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.validators import EmailValidator
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier for authentication."""

    def _create_user(self, email, password=None, **extra_fields):
        """Handles the common logic for user creation."""
        if not email:
            raise ValueError(_("The Email field is required"))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self._create_user(email, password, **extra_fields)

ROLE_ADMIN = 'admin'
ROLE_OWNER = 'owner'


class User(AbstractUser):
    """Custom user model with email for authentication instead of username."""

    ROLE_CHOICES = (
        (ROLE_OWNER, "Owner"),
        (ROLE_ADMIN, "Administrator"),  # Добавлена роль администратора
    )

    username = None  # Remove username field as it's no longer needed
    email = models.EmailField(
        _("email address"),
        validators=[EmailValidator(_("Enter a valid email address."))],
        unique=True
    )
    phone_number = PhoneNumberField(_("Номер телефона"), blank=True)
    full_name = models.CharField('ФИО', max_length=100, blank=False)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True
    )
    tg_chat_id = models.BigIntegerField('chat id в телеграмме',unique=True, blank=True, null=True)
    venue = models.ForeignKey(
        'venues.Venue', on_delete=models.CASCADE, related_name='users',
        verbose_name="Заведение", blank=True, null=True
    )
    spot = models.ForeignKey(
        'venues.Spot', on_delete=models.CASCADE, related_name='users',
        blank=True, null=True, verbose_name="Точка заведения"
    )

    USERNAME_FIELD = "email"  # Use email as the unique identifier
    REQUIRED_FIELDS = ['full_name']  # Required fields when creating a superuser

    objects = UserManager()

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.email} - {self.full_name}"


