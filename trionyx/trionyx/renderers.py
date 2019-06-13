"""
trionyx.trionyx.renderers
~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""


def render_level(model, *args, **kwargs):
    """Render level as label"""
    mapping = {
        10: 'info',
        20: 'info',
        30: 'warning',
        40: 'danger',
        50: 'danger',
    }

    return '<span class="label label-{}">{}</span>'.format(
        mapping.get(model.level, 'secondary'),
        model.get_level_display().upper()
    )
