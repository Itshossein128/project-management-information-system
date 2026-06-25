"""
Blueprint-aligned User model (Domain 1: Master Data).
UUID primary key; login via username or mobile.
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message=_('Phone number must be 9-15 digits, optionally starting with +.'),
)


class UserStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    SUSPENDED = 'suspended', 'Suspended'


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('status', UserStatus.ACTIVE)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', UserStatus.ACTIVE)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=120, blank=True, default='')
    username = models.CharField(max_length=60, unique=True)
    email = models.EmailField(max_length=120, blank=True, null=True)
    mobile = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[phone_regex],
        help_text='Mobile number; may be used for login',
    )
    organization = models.CharField(max_length=120, blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
    )
    created_at = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        db_table = 'users'

    def __str__(self):
        return self.full_name or self.username

    def get_full_name(self):
        return self.full_name or self.username

    def get_short_name(self):
        return self.username

    @property
    def phone_number(self):
        """Backward compatibility alias for mobile."""
        return self.mobile or ''


class PasswordResetToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'expires_at']),
        ]
