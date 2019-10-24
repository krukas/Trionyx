"""
trionyx.trionyx.auditlog
~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
import logging

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save, post_save, post_delete
from django.utils.translation import ugettext_lazy as _
from trionyx import models
from trionyx.config import models_config
from trionyx.trionyx.models import AuditLogEntry
from trionyx.utils import get_current_request
from trionyx.trionyx.layouts import auditlog as auditlog_layout
from trionyx.views import tabs
from trionyx.renderer import renderer

logger = logging.getLogger(__name__)


def model_instance_diff(old, new):
    """Create diff of two model instances"""
    diff = {}

    config = models_config.get_config(new if new else old)
    ignore_fields = config.auditlog_ignore_fields if config.auditlog_ignore_fields else []
    fields = [field for field in config.get_fields() if field.name not in ignore_fields]

    for field in fields:
        old_value = get_field_value(old, field)
        new_value = get_field_value(new, field)

        if old_value != new_value:
            diff[field.name] = (
                get_rendered_value(config.model, field.name, old_value),
                get_rendered_value(config.model, field.name, new_value),
            )

    return diff if diff else None


def get_field_value(obj, field):
    """Get field value that can be used to compare"""
    if isinstance(field, models.DateTimeField):
        try:
            value = field.to_python(getattr(obj, field.name, None))
            if value is not None and settings.USE_TZ and not timezone.is_naive(value):
                value = timezone.make_naive(value, timezone=timezone.utc)
            return value
        except ObjectDoesNotExist:
            pass
    elif isinstance(field, models.DecimalField):
        try:
            return field.to_python(getattr(obj, field.name, None))
        except TypeError:
            pass
    else:
        try:
            return getattr(obj, field.name, None)
        except ObjectDoesNotExist:
            pass

    return field.default if field.default is not models.NOT_PROVIDED else None


def get_rendered_value(ModelClass, field_name, value):
    """Render value for given model class and field"""
    model = ModelClass(**{field_name: value})
    return renderer.render_field(model, field_name)


def create_log(instance, changes, action):
    """Create a new log entry"""
    AuditLogEntry.objects.create(
        content_object=instance,
        object_verbose_name=str(instance),
        action=action,
        changes=changes,
        user=get_current_request().user if get_current_request() and not get_current_request().user.is_anonymous else None
    )


def log_add(sender, instance, created, **kwargs):
    """Log model add"""
    try:
        if created:
            changes = model_instance_diff(None, instance)
            if changes:
                create_log(instance, changes, AuditLogEntry.ACTION_ADDED)
    except Exception as e:
        logger.exception(e)


def log_change(sender, instance, **kwargs):
    """Log model update"""
    try:
        if instance.pk is not None:
            try:
                old = sender.objects.get(pk=instance.pk)
            except sender.DoesNotExist:
                return

            changes = model_instance_diff(old, instance)
            if changes:
                create_log(instance, changes, AuditLogEntry.ACTION_CHANGED)
    except Exception as e:
        logger.exception(e)


def log_delete(sender, instance, **kwargs):
    """Log model delete"""
    try:
        if instance.pk is not None:
            changes = model_instance_diff(instance, None)
            if changes:
                create_log(instance, changes, AuditLogEntry.ACTION_DELETED)
    except Exception as e:
        logger.exception(e)


def init_auditlog():
    """Init auditlog"""
    for config in models_config.get_all_configs(False):
        if config.auditlog_disable or (not config.is_trionyx_model and not config.has_config('auditlog_disable')):
            continue

        post_save.connect(log_add, sender=config.model, dispatch_uid=(log_add, config.model, post_save))
        pre_save.connect(log_change, sender=config.model, dispatch_uid=(log_change, config.model, pre_save))
        post_delete.connect(log_delete, sender=config.model, dispatch_uid=(log_delete, config.model, post_delete))

        @tabs.register(config.model, code='history', name=_('History'), order=999)
        def layout(obj):
            return auditlog_layout(obj)
