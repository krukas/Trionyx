"""
trionyx.trionyx.models
~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import hashlib
import traceback
from contextlib import contextmanager

from celery import current_app
from celery.app.control import Control
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes import fields
from django.utils import timezone
from django.conf import settings
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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
    last_online = models.DateTimeField(_('Last online'), blank=True, null=True)
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
        models.get_class(UserAttribute).objects.set_attribute(self, code, value)

    def get_attribute(self, code, default=None):
        """Get user attribute"""
        return models.get_class(UserAttribute).objects.get_attribute(self, code, default)

    @contextmanager
    def locale_override(self):
        """Override locale settings to user settings"""
        with translation.override(self.language), timezone.override(self.timezone):
            yield

    def send_email(self, subject, body='', html_template=None, template_context=None, files=None):
        """Send email to user"""
        if not body and not html_template:
            raise Exception('You must supply a body or/and html_template')

        with self.locale_override():
            message = EmailMultiAlternatives(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.email]
            )

            if html_template:
                message.attach_alternative(
                    render_to_string(html_template, template_context if template_context else {}),
                    "text/html")

        if files:
            for file in files:
                message.attach(file.name, file.read())

        return message.send()


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
# System variable
# =============================================================================
class SystemVariable(models.Model):
    """Model to store system wide variable like account/invoice counter

    Never use this model directly and use the trionyx.config.variables
    """

    code = models.CharField(max_length=128, unique=True)
    value = models.JSONField()

    def __str__(self):
        """System variable representation"""
        return self.code


# =============================================================================
# Logging
# =============================================================================
class LogManager(models.BaseManager):
    """Log manager"""

    def create_log_entry_by_record(self, record):
        """Create log entry by `logging.LogRecord`"""
        if record.name == 'celery.app.trace':
            # Remove celery task id, to make same errors match
            record.args['id'] = ''

        log_hash = hashlib.md5(str(' '.join(str(x) for x in [
            record.pathname,
            record.lineno,
            record.getMessage(),
        ])).encode()).hexdigest()

        log, _ = self.get_or_create(log_hash=log_hash, defaults={
            'level': record.levelno,
            'message': record.getMessage(),
            'file_path': record.pathname,
            'file_line': record.lineno,
            'last_event': timezone.now(),
        })

        if record.exc_info and not log.traceback:
            log.traceback = ''.join(traceback.TracebackException(
                *record.exc_info
            ).format())
        if not record.exc_info and not log.traceback:
            # Create traceback and remove last items from log library
            new_trace = 'Traceback stack (with the logging removed):\n'
            for line in traceback.format_stack():
                if '/logging/__init__.py' in line:
                    break
                new_trace += line
            log.traceback = new_trace

        request = get_current_request()
        entry = LogEntry.objects.create(
            log=log,
            log_time=timezone.now(),
            user=request.user if request and not request.user.is_anonymous else None,
            path=request.path if request else '',
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

    objects = LogManager()  # type: ignore

    class Meta:
        """Model meta description"""

        verbose_name = _('Log')
        verbose_name_plural = _('Logs')


class LogEntry(models.Model):
    """Log entry event"""

    log = models.ForeignKey(Log, models.CASCADE, related_name='entries')
    log_time = models.DateTimeField(_('Log time'))

    user = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, verbose_name=_('User'))
    path = models.TextField(_('Path'), default='')
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


# =============================================================================
# Task
# =============================================================================
class Task(models.BaseModel):
    """Task model"""

    SCHEDULED = 10
    QUEUE = 20
    LOCKED = 30
    RUNNING = 40
    COMPLETED = 50
    FAILED = 99

    STATUS_CHOICES = (
        (SCHEDULED, _('Scheduled')),
        (QUEUE, _('Queue')),
        (LOCKED, _('Locked')),
        (RUNNING, _('Running')),
        (COMPLETED, _('Completed')),
        (FAILED, _('Failed')),
    )

    celery_task_id = models.CharField(max_length=64, unique=True)
    status = models.IntegerField(_('Status'), choices=STATUS_CHOICES, default=QUEUE)
    identifier = models.CharField(_('Identifier'), max_length=255, default='not_set')
    description = models.TextField(_('Description'), default='')

    progress = models.PositiveIntegerField(_('Progress'), default=0)
    progress_output = models.JSONField(_('Progress output'), default=list)

    scheduled_at = models.DateTimeField(_('Scheduled at'), blank=True, null=True)
    started_at = models.DateTimeField(_('started at'), blank=True, null=True)
    execution_time = models.IntegerField(_('Execution time'), default=0)
    result = models.TextField(_('Result'), blank=True, default='')

    user = models.ForeignKey(
        User, models.SET_NULL, blank=True, null=True,
        verbose_name=_('Started by'))
    object_type = models.ForeignKey(
        'contenttypes.ContentType',
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='+',
        verbose_name=_('Object type')
    )
    object_id = models.BigIntegerField(_('Object ID'), blank=True, null=True)
    object = fields.GenericForeignKey('object_type', 'object_id')
    object_verbose_name = models.TextField(_('Object name'), blank=True, default='')

    class Meta:
        """Model meta description"""

        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')

    def cancel_celery_task(self, kill=False):
        """
        Make sure we cancel the task (if in queue/scheduled).
        :param: kill Also kill the task if it's running, defaults to False.
        """
        celery_control = Control(current_app)
        celery_control.revoke(task_id=self.celery_task_id, terminate=kill)
