"""
trionyx.core.models
~~~~~~~~~~~~~~~~

Core models

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.urls import reverse

from trionyx.config import models_config


class BaseManager(models.Manager):
    """model base manager for all Trionyx models"""

    def get_queryset(self):
        """Give qeuryset where deleted items are filtered"""
        return super().get_queryset().filter(deleted=False)
        

class BaseModel(models.Model):
    """Base model for all Trionyx models"""

    objects = BaseManager()

    created_at = models.DateTimeField(auto_now_add=True)
    """Created at field, date is set when model is created"""

    updated_at = models.DateTimeField(auto_now=True)
    """Update at field, date is set when model is saved"""

    deleted = models.BooleanField(default=False)
    """Deleted field, object is soft deleted"""

    class Meta:
        """Meta information for BaseModel"""

        abstract = True
        default_permissions = ('read', 'add', 'change', 'delete')

    @classmethod
    def get_fields(cls, inlcude_base=False, include_id=False):
        for field in cls._meta.fields:
            if not include_id and field.name == 'id':
                continue
            if not inlcude_base and field.name in ['created_at', 'updated_at', 'deleted']:
                continue
            yield field

    def __str__(self):
        """Give verbose name of object"""
        app_label = self._meta.app_label
        model_name = type(self).__name__
        verbose_name = models_config.get_config(self).verbose_name
        return verbose_name.format(model_name=model_name, app_label=app_label, **self.__dict__)


    def get_absolute_url(self):
        return reverse('trionyx:model-view', kwargs={
            'app': self._meta.app_label,
            'model': self._meta.model_name,
            'pk': self.id
        })


class UserManager(BaseUserManager, BaseManager):
    def _create_user(self, email, password, is_superuser, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            password=password,
            is_active=True,
            is_superuser=is_superuser, last_login=now,
            date_joined=now,
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        return self._create_user(email, password, True, **extra_fields)

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=64, blank=True, default='')
    last_name = models.CharField(max_length=64, blank=True, default='')
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    avatar = models.ImageField(blank=True, upload_to='avatars/', default='')

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def get_full_name(self):
        if self.first_name and self.last_name:
            return "{} {}".format(self.first_name, self.last_name)
        return self.email

    def get_short_name(self):
        if self.first_name:
            return self.first_name
        return self.email

    def __str__(self):
        return self.email
