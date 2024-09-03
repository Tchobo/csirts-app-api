from django.db import models
from django.conf import settings
# Create your models here.
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

import uuid
import os




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
    description = models.TextField(blank=True)
    location = models.JSONField(null=False, blank=False)
    contact  = models.CharField(max_length=30, null=True, blank=True)
    website = models.CharField(max_length=100)
    image = models.ImageField(null=True, upload_to=csirt_image_file_path)

    def __str__(self):
        return self.name
