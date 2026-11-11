from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError

# Create your models here.


class CustomUsermanager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен!")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        phone_number = extra_fields.get("phone_number")
        if not phone_number:
            raise ValueError("Superuser должен иметь номер телефона!")
        if not str(phone_number).startswith("996"):
            raise ValidationError("Номер телефона должен начинаться с 996!")
        return self.create_superuser(email, password, **extra_fields)


def validate_phone_996(value):
    if not str(value).startswith("996"):
        raise ValidationError("Номер телефона должен начинаться с 996!")


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=20, blank=True, null=True, validators=[validate_phone_996]
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        verbose_name="groups",
        related_query_name="customuser",
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",
        blank=True,
        help_text="The permissions granted to this user.",
        verbose_name="permissions",
        related_query_name="customuser",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUsermanager()

    def __str__(self):
        return self.email
