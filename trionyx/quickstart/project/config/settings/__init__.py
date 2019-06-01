"""Project settings"""
from trionyx.settings import get_env_var


if get_env_var('DEBUG', False):
    from .dev import *  # noqa: F403 F401
else:
    from .live import *  # noqa: F403 F401
