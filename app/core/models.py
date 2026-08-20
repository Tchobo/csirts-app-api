from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
# Create your models here.
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

import uuid
import os


def validate_csirt_location(value):
    """Model-level validator for the Csirt.location JSONField.

    Runs on model.full_clean() — which is called by the Django admin
    ModelForm and by any explicit .full_clean() call. This means the same
    validation kicks in regardless of the write path (API, admin, shell,
    fixtures), preventing case-mismatched keys or string coords from
    slipping into the database.

    Note: this validator does NOT mutate `value` (validators aren't allowed
    to). Coercion / normalisation happens in the DRF serializer path.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            "location must be a JSON object with latitude and longitude."
        )

    lower_map = {str(k).lower(): v for k, v in value.items()}
    for key in ("latitude", "longitude"):
        if key not in lower_map:
            raise ValidationError(f"location.{key} is required.")

    try:
        lat = float(str(lower_map["latitude"]).replace(",", "."))
        lng = float(str(lower_map["longitude"]).replace(",", "."))
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            "location.latitude and location.longitude must be numeric."
        ) from exc

    if not (-90 <= lat <= 90):
        raise ValidationError(f"latitude must be between -90 and 90 (got {lat}).")
    if not (-180 <= lng <= 180):
        raise ValidationError(f"longitude must be between -180 and 180 (got {lng}).")


def csirt_image_file_path(instance, filename):
    """Generating file path for new csirt image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'csirt', filename)

# Create your models here.

class UserManager(BaseUserManager):
    """ Manager for User"""
    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('You must have an email adresse.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser =True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """ User in the system."""
    email = models.EmailField(max_length=225, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'



class Csirt(models.Model):
    """Csirt Object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    location = models.JSONField(
        null=False, blank=False, validators=[validate_csirt_location]
    )
    contact  = models.CharField(max_length=30, null=True, blank=True)
    website = models.CharField(max_length=100)
    image = models.ImageField(null=True, upload_to=csirt_image_file_path)

    def __str__(self):
        return self.name
