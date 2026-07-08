"""
Custom User model with phone_number as the unique identifier.
No username; uses first_name + last_name for display.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone


# A validator instance for validating phone numbers using regex.
# It ensures phone numbers are 9-15 digits long and can optionally start with a '+'.
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be 9-15 digits, optionally starting with +"
)


class CustomUserManager(BaseUserManager):
    """Manager for custom User model using phone_number."""

    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Creates and saves a standard User with the given phone number and password.

        Args:
            phone_number: The unique phone number for the user.
            password: The user's password (will be hashed).
            extra_fields: Additional fields for the User model.

        Returns:
            The created User instance.
        """
        if not phone_number:
            raise ValueError("Phone number is required")
        extra_fields.setdefault("is_active", True)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """
        Creates and saves a Superuser with the given phone number and password.
        Ensures that `is_staff` and `is_superuser` are set to True.

        Args:
            phone_number: The unique phone number for the superuser.
            password: The superuser's password.
            extra_fields: Additional fields for the User model.

        Returns:
            The created superuser instance.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(phone_number, password, **extra_fields)


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

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        """Returns a string representation of the user, preferring full name over phone number."""
        return self.get_full_name() or self.phone_number

    def get_full_name(self):
        """
        Returns the user's full name by concatenating first_name and last_name.
        If both are blank, it falls back to the phone number.
        """
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.phone_number

    def get_short_name(self):
        """
        Returns the user's short name (first name).
        If first name is blank, it falls back to the phone number.
        """
        return self.first_name or self.phone_number
