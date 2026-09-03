import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for email-based user creation.
    Django's default manager uses 'username'; we use 'email'.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hashes the password (PBKDF2)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("status", "active")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for SkillMatch.
    Replaces Django's default username-based User with email-based login.
    """
    ROLE_CHOICES = [
        ("student", "Student"),
        ("company", "Company"),
        ("admin", "Admin"),
    ]
    STATUS_CHOICES = [
        ("pending_email", "Pending Email Verification"),
        ("pending_admin", "Pending Admin Approval"),
        ("active", "Active"),
        ("rejected", "Rejected"),
        ("suspended", "Suspended"),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending_email")
    
    # Django required fields for admin compatibility
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # Tell Django to use email instead of username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"


class EmailVerificationToken(models.Model):
    """
    Stores the token sent via email when a user registers.
    Single-use, no expiry stored here (checked in view logic).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)


class PasswordResetToken(models.Model):
    """
    Stores the token for password reset.
    1-hour expiry checked in view logic.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)


class OTPLog(models.Model):
    """
    Stores OTP codes for admin two-factor login.
    5-minute expiry checked in view logic.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)