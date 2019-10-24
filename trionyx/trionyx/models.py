"""
trionyx.trionyx.models
~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import hashlib
import traceback

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes import fields
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from trionyx import models
from trionyx.utils import get_current_request
from trionyx.data import TIMEZONES


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


def default_language():
    """Return default language from settings, prevent new migrations if setting changed"""
    return settings.LANGUAGE_CODE


def default_timezone():
    """Return default timezone from settings, prevent new migrations if setting changed"""
    return settings.TIME_ZONE


class User(models.BaseModel, AbstractBaseUser, PermissionsMixin):
    """User model"""

    email = models.EmailField(_('Email'), max_length=255, unique=True)
    first_name = models.CharField(_('First name'), max_length=64, blank=True, default='')
    last_name = models.CharField(_('Last name'), max_length=64, blank=True, default='')
    is_active = models.BooleanField(_('Active'), default=True)
    date_joined = models.DateTimeField(_('Date joined'), default=timezone.now)
    last_online = models.DateTimeField(_('Last online'), blank=None, null=True)
    avatar = models.ImageField(_('Avatar'), blank=True, upload_to='avatars/', default='')

    language = models.CharField(_('Language'), max_length=6, choices=settings.LANGUAGES, default=default_language)
    timezone = models.CharField(_('Timezone'), max_length=32, choices=TIMEZONES, default=default_timezone)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        """Model meta description"""

        verbose_name = _('User')
        verbose_name_plural = _('Users')

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

    def set_attribute(self, code, value):
        """Set user attribute"""
        UserAttribute.objects.set_attribute(self, code, value)

    def get_attribute(self, code, default=None):
        """Get user attribute"""
        return UserAttribute.objects.get_attribute(self, code, default)


class UserAttributeManager(models.Manager):
    """User attribute manager"""

    def set_attribute(self, user, code, value):
        """Set attribute for user"""
        self.update_or_create(user=user, code=code, defaults={'value': value})

    def get_attribute(self, user, code, default=None):
        """Get attribute for user"""
        try:
            return self.get(user=user, code=code).value
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


# =============================================================================
# Logging
# =============================================================================
class LogManager(models.BaseManager):
    """Log manager"""

    def create_log_entry_by_record(self, record):
        """Create log entry by `logging.LogRecord`"""
        log_hash = hashlib.md5(str(' '.join(str(x) for x in [
            record.pathname,
            record.lineno,
            record.msg,
        ])).encode()).hexdigest()

        log, _ = self.get_or_create(log_hash=log_hash, defaults={
            'level': record.levelno,
            'message': record.msg,
            'file_path': record.pathname,
            'file_line': record.lineno,
            'last_event': timezone.now(),
        })

        if record.exc_info and not log.traceback:
            log.traceback = ''.join(traceback.TracebackException(
                *record.exc_info
            ).format())

        request = get_current_request()
        entry = LogEntry.objects.create(
            log=log,
            log_time=timezone.now(),
            user=request.user if request and not request.user.is_anonymous else None,
            user_agent=request.META.get('HTTP_USER_AGENT') if request else '',
        )

        log.last_event = entry.log_time
        log.log_count = log.entries.count()
        log.save()


class Log(models.BaseModel):
    """Log"""

    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    LEVEL_CHOICES = [
        (CRITICAL, _('Critical')),
        (ERROR, _('Error')),
        (WARNING, _('Warning')),
        (INFO, _('Info')),
        (DEBUG, _('Debug')),
        (NOTSET, _('Not set')),
    ]

    log_hash = models.CharField(_('Log hash'), max_length=32)
    level = models.IntegerField(_('Level'), choices=LEVEL_CHOICES)
    message = models.TextField(_('Message'))
    file_path = models.CharField(_('File path'), max_length=256)
    file_line = models.IntegerField(_('File line'))
    traceback = models.TextField(_('Traceback'), default='')

    last_event = models.DateTimeField(_('Last event'))
    log_count = models.IntegerField(_('Log count'), default=1)

    objects = LogManager()

    class Meta:
        """Model meta description"""

        verbose_name = _('Log')
        verbose_name_plural = _('Logs')


class LogEntry(models.Model):
    """Log entry event"""

    log = models.ForeignKey(Log, models.CASCADE, related_name='entries')
    log_time = models.DateTimeField(_('Log time'))

    user = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, verbose_name=_('User'))
    user_agent = models.TextField(_('User agent'), default='')

    class Meta:
        """Model meta description"""

        verbose_name = _('Log entry')
        verbose_name_plural = _('Log entries')


class AuditLogEntry(models.BaseModel):
    """Auditlog model"""

    ACTION_ADDED = 10
    ACTION_CHANGED = 20
    ACTION_DELETED = 30

    action_choices = [
        (ACTION_ADDED, _('Added')),
        (ACTION_CHANGED, _('Changed')),
        (ACTION_DELETED, _('Deleted')),
    ]

    content_type = models.ForeignKey('contenttypes.ContentType', models.CASCADE, related_name='+')
    object_id = models.BigIntegerField(blank=True, null=True)
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    object_verbose_name = models.TextField(default='', blank=True)

    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, related_name='+')
    action = models.IntegerField(choices=action_choices)
    changes = models.JSONField()

    class Meta:
        """Model meta description"""

        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
