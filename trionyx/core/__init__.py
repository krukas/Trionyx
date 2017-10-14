"""
trionyx.core
~~~~~~~~~~~~

Core app for Trionyx

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""

default_app_config = 'trionyx.core.apps.CoreConfig'


def jwt_response_payload_handler(token, user, request):
    """Add extra data to auth payload"""
    return {
        'token': token,
        'user': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'avatar': 'base64 image',
        },
        'permissions': user.get_all_permissions()
    }
