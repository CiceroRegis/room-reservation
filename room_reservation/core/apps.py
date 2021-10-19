from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    name = 'room_reservation.core'
    verbose_name = _('Structure and Organization')
