from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReservationConfig(AppConfig):
    name = 'room_reservation.reservation'
    verbose_name = _('Reservation')

