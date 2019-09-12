from rest_framework import serializers
from trionyx.trionyx.models import User
from trionyx.api.serializers import register


@register(User)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'verbose_name']