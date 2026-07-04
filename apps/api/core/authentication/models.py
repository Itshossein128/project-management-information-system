"""
Custom User model with phone_number as the unique identifier.
No username; uses first_name + last_name for display.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone


phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be 9-15 digits, optionally starting with +"
)


# Class representing CustomUserManager
class CustomUserManager(BaseUserManager):
    """Manager for custom User model using phone_number."""

    # Function to handle create user
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
        extra_fields.setdefault("is_active", True)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Function to handle create superuser
    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(phone_number, password, **extra_fields)


# Class representing User
class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model.
    - Uses phone_number as the unique identifier (login field).
    - No username or email required.
    - Display name: first_name + last_name.
    """
    phone_number = models.CharField(
        max_length=17,
        unique=True,
        validators=[phone_regex],
        help_text="Unique phone number for login"
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # Class representing Meta
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    # Function to handle   str
    def __str__(self):
        return self.get_full_name() or self.phone_number

    # Function to handle get full name
    def get_full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.phone_number

    # Function to handle get short name
    def get_short_name(self):
        return self.first_name or self.phone_number
