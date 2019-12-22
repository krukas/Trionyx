from trionyx.trionyx.models import User
from trionyx.api import serializers


@serializers.register
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'verbose_name']