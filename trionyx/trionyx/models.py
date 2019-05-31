"""
trionyx.trionyx.models
~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from trionyx import models
from django.utils import timezone


# =============================================================================
# User models
# =============================================================================
class UserManager(BaseUserManager, models.BaseManager):
    """Manager for user"""

    def _create_user(self, email, password, is_superuser, **extra_fields):
        """Create new user"""
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
        """Create standard user"""
        return self._create_user(email, password, False, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create super user"""
        return self._create_user(email, password, True, **extra_fields)

    def get_queryset(self):
        """Get queryset default filter inactive users"""
        return super().get_queryset().filter(is_active=True)


class User(models.BaseModel, AbstractBaseUser, PermissionsMixin):
    """User model"""

    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=64, blank=True, default='')
    last_name = models.CharField(max_length=64, blank=True, default='')
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    avatar = models.ImageField(blank=True, upload_to='avatars/', default='')

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def get_full_name(self):
        """Get full username if no name is set email is given"""
        if self.first_name and self.last_name:
            return "{} {}".format(self.first_name, self.last_name)
        return self.email

    def get_short_name(self):
        """Get short name if no name is set email is given"""
        if self.first_name:
            return self.first_name
        return self.email

    def __str__(self):
        """User representation"""
        return self.email


class UserAttributeManager(models.Manager):
    """User attribute manager"""

    def set_attribute(self, code, value):
        """Set attribute for user"""
        attr, _ = self.get_or_create(code=code)
        attr.value = value
        attr.save()

    def get_attribute(self, code, default=None):
        """Get attribute for user"""
        try:
            return self.get(code=code).value
        except models.ObjectDoesNotExist:
            return default


class UserAttribute(models.Model):
    """User attribute to store system values for user"""

    user = models.ForeignKey(User, models.CASCADE, related_name='attributes')
    code = models.CharField(max_length=128, null=False)
    value = models.JSONField()

    objects = UserAttributeManager()

    class Meta:
        """Model meta description"""

        unique_together = ('user', 'code')

    def __str__(self):
        """User Attribute representation"""
        return self.code
