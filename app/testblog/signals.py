from django.dispatch import receiver
from trionyx.signals import can_change

from .models import Post


@receiver(can_change, sender=Post)
def send_pickup_time(sender, instance, **kwargs):
    return instance.id % 2 == 0