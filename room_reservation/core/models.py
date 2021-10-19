import logging
import quopri
import random
import textwrap
import threading
import uuid
from datetime import timedelta
from email.mime.text import MIMEText

from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import models
from django.utils.translation import gettext_lazy as _
from filebrowser.fields import FileBrowseField

logger = logging.getLogger('django')


class User(AbstractUser):
    class Meta:
        db_table = 'User'
        verbose_name = _('User')


class Notification(models.Model):
    NOTIFICATION_MODEL_ACTION = (
        ('reservation-saved', _('Notify when reservation approved')),
    )

    class Meta:
        db_table = 'Notification'
        verbose_name = _('Notification')

    action = models.CharField(max_length=200, choices=NOTIFICATION_MODEL_ACTION, verbose_name=_('Action'))
    user = models.ForeignKey('User', on_delete=models.DO_NOTHING, verbose_name=_('User'))

    def __str__(self):
        return '@{0} - {1}'.format(self.user.username, self.user.get_full_name())


class RoomType(models.Model):
    class Meta:
        db_table = 'RoomType'
        verbose_name = _('Room Type')
        verbose_name_plural = _('Room Type')

    name = models.CharField(max_length=45, verbose_name=_('Name'))
    createAt = models.DateTimeField(null=False, blank=False, editable=False, auto_now_add=True)

    def __str__(self):
        return self.name


class RoomProperty(models.Model):
    class Meta:
        db_table = 'RoomProperty'
        verbose_name = _('RoomProperty')
        verbose_name_plural = _('RoomProperty')

    name = models.CharField(max_length=45, verbose_name=_('Name'))
    value = models.CharField(max_length=45, null=True, blank=True, verbose_name=_('amount'))
    createAt = models.DateTimeField(null=False, blank=False, editable=False, auto_now_add=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    class Meta:
        db_table = 'Room'
        verbose_name = _('Room')

    roomType = models.ForeignKey(RoomType, verbose_name=_('Room Type'), on_delete=models.DO_NOTHING)
    linkRoom = models.ManyToManyField('Room', blank=True, editable=False, verbose_name=_('Linked room'),
                                      related_name='linked_rooms')
    allowRoomProperty = models.BooleanField(default=False, verbose_name=_('Allow room property'),
                                            help_text=_('if this option is checked the room properties will be shown.'))
    videoConferecingOption = models.BooleanField(default=False, verbose_name=_('video conferecing option'),
                                                 help_text=_('if this option is checked '
                                                             'Time limit for schedules of up to 4 hours per period ('
                                                             'morning and afternoon)'))

    roomProperty = models.ManyToManyField(RoomProperty, related_name='room_property', verbose_name=_('Room Property'))
    name = models.CharField(max_length=200, null=False, blank=False, verbose_name=_('Name'))
    numberPeople = models.IntegerField(default=0, null=True, blank=False, verbose_name=_('People number'))
    numberPeopleAggregated = models.IntegerField(default=0, null=True, blank=False, editable=False)
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    cover = FileBrowseField('Cover', max_length=200, null=True, blank=True)
    allowRoomType = models.BooleanField(default=False, verbose_name=_('Room model type'),
                                        help_text=_('if this option is checked the Room model type will be shown.'))
    autoReserve = models.BooleanField(default=True, verbose_name=_('Auto Reserve'))
    isLinkedRoom = models.BooleanField(default=False, editable=False)
    updateAt = models.DateTimeField(null=False, blank=False, editable=False, auto_now=True)
    createAt = models.DateTimeField(null=False, blank=False, editable=False, auto_now_add=True)

    def __str__(self):
        return self.name

    # return sum linkedRoom  with numble people
    def save(self, *args, **kwargs):
        total_sum = RoomLink.objects.filter(room=self).aggregate(models.Sum('linkRoom__numberPeople')).get(
            'linkRoom__numberPeople__sum', 0)
        self.numberPeopleAggregated = (total_sum if total_sum else 0) + (self.numberPeople if self.numberPeople else 0)
        super(Room, self).save(*args, **kwargs)


class RoomLink(models.Model):
    LOCATIONS = (
        ('LEFT', _('Left')),
        ('RIGHT', _('Right')),
        ('TOP', _('Top')),
        ('Down', _('Down')),
    )

    class Meta:
        db_table = 'RoomLink'
        verbose_name = _('Room Link')

    room = models.ForeignKey('Room', on_delete=models.DO_NOTHING, related_name='room_link')
    linkRoom = models.ForeignKey('Room', null=True, verbose_name=_('Room'), related_name='room_linked',
                                 on_delete=models.DO_NOTHING)
    location = models.CharField(max_length=20, null=True, blank=True, editable=False, choices=LOCATIONS,
                                verbose_name=_('Room location'))
    position = models.IntegerField(verbose_name=_('Room position'))
    createAt = models.DateTimeField(null=False, blank=False, editable=False, auto_now_add=True)

    def __str__(self):
        return self.linkRoom.name


class RoomImage(models.Model):
    class Meta:
        db_table = 'RoomImage'
        verbose_name = _('room images')

    room = models.ForeignKey(Room, related_name='room_images', on_delete=models.CASCADE, verbose_name=_('Room'))
    fileSrc = FileBrowseField(_('Image'), max_length=200)
    createAt = models.DateTimeField(null=False, blank=False, editable=False, auto_now_add=True)


class ReservationType(models.Model):
    class Meta:
        db_table = 'ReservationType'
        verbose_name = _('Reservation Type')
        verbose_name_plural = _('Reservation Type')

    name = models.CharField(max_length=45, verbose_name=_('Name'))
    createAt = models.DateTimeField(null=False, blank=False, editable=False, auto_now_add=True)

    def __str__(self):
        return self.name


class ReservationPublic(models.Model):
    class Meta:
        db_table = 'ReservationPublic'
        verbose_name = _('Reservation Public')
        verbose_name_plural = _('Reservation Public')

    name = models.CharField(max_length=45, verbose_name=_('Name'))
    createAt = models.DateTimeField(null=False, blank=False, editable=False, auto_now_add=True)

    def __str__(self):
        return self.name


class ReservationRoomFormat(models.Model):
    class Meta:
        db_table = 'ReservationRoomFormat'
        verbose_name = _('Reservation Room Formats')
        verbose_name_plural = _('Reservation Room Formats')

    name = models.CharField(max_length=45, verbose_name=_('Name'))
    createAt = models.DateTimeField(null=False, blank=False, editable=False, auto_now_add=True)

    def __str__(self):
        return self.name


class ReservationResource(models.Model):
    class Meta:
        db_table = 'ReservationResource'
        verbose_name_plural = _('Reservation resources')

    name = models.CharField(max_length=45, verbose_name=_('Name'))
    createAt = models.DateTimeField(null=False, blank=False, editable=False, auto_now_add=True)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    class Meta:
        db_table = 'Reservation'
        verbose_name = _('Reservation')

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_('User'))
    room = models.ForeignKey(Room, on_delete=models.DO_NOTHING, verbose_name=_('Room'))

    linkedReservation = models.ForeignKey('Reservation', null=True, blank=True, editable=False,
                                          on_delete=models.CASCADE, verbose_name=_('Linked Room'),
                                          related_name='linked_rooms')

    reservationType = models.ForeignKey(ReservationType, null=True, default=None, on_delete=models.DO_NOTHING,
                                        verbose_name=_('Reservation Type'))
    reservationPublic = models.ForeignKey(ReservationPublic, null=True, default=None, on_delete=models.DO_NOTHING,
                                          verbose_name=_('Reservation Public'))
    reservationRoomFormat = models.ForeignKey(ReservationRoomFormat, null=True, blank=True, default=None,
                                              on_delete=models.DO_NOTHING, verbose_name=_('Reservation Room Format'))
    reservationResource = models.ManyToManyField(ReservationResource, blank=True, editable=False,
                                                 verbose_name=_('Reservation resources'))

    calendarUUID = models.UUIDField(default=uuid.uuid4, editable=False)
    calendarOwnerTID = models.IntegerField(default=random.randrange(-214748364, 2147483647), editable=False)

    name = models.CharField(max_length=60, null=True, default=None, verbose_name=_('Event name'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    dateInitial = models.DateTimeField(verbose_name=_('Initial date'))
    dateFinal = models.DateTimeField(verbose_name=_('Final date'))
    numberOfGuests = models.IntegerField(default=0, verbose_name=_('Number of guests'))
    guests = models.TextField(null=True, blank=True, verbose_name=_('Guests'))
    booked = models.BooleanField(null=True, verbose_name=_('Booked'))
    isCanceled = models.BooleanField(default=False, editable=False)
    isLinkedRoom = models.BooleanField(default=False, editable=False)
    updateAt = models.DateTimeField(null=False, blank=False, editable=False, auto_now=True)
    createAt = models.DateTimeField(null=False, blank=False, editable=False, auto_now_add=True)

    def __str__(self):
        return self.name

    def date_initial(self):
        _date = self.dateInitial - timedelta(hours=2)
        return _date.strftime('%d/%m/%Y %H:%M')

    def date_final(self):
        _date = self.dateFinal - timedelta(hours=2)
        return _date.strftime('%d/%m/%Y %H:%M')

    def reservation_resource_list(self):
        return ', '.join([str(i) for i in self.reservationResource.all()])

    def save(self, *args, **kwargs):
        super(Reservation, self).save(*args, **kwargs)
        if not self.isLinkedRoom:
            self.start = threading.Thread(target=self.__send_invite_ics, args=()).start()

        if self.booked is True and self.isLinkedRoom is False:
            threading.Thread(target=self.__notify_user_action_saved, args=()).start()

    def delete(self, *args, **kwargs):
        threading.Thread(target=self.__send_invite_ics, args=()).start()
        super(self.__class__, self).delete(*args, **kwargs)

    def __send_invite_ics(self):
        if not self.booked:
            logger.info('The reservation is not booked')
            return
        if not self.user.email:
            logger.warning('User email is empty')
            return

        try:
            email_message = '\n'.join([
                'Agendamento realizado',
                '{0}: {1}'.format('Data inicial', self.dateInitial.strftime('%d/%m/%Y %H:%M')),
                '{0}: {1}'.format('Data final', self.dateFinal.strftime('%d/%m/%Y %H:%M')),
                '{0}: {1}'.format('Quantidade de participantes', self.numberOfGuests),
                '{0}: {1}'.format('Espaço', self.room.name),
                '{0}: {1}'.format('Objetivo da reserva', self.reservationType.name),
                '{0}: {1}'.format('Descrição', self.description),
            ])
            guests = self.guests.split(';') if self.guests else []
            email = EmailMultiAlternatives(
                '{0} - {1}'.format(self.name, 'cancelado' if self.isCanceled else 'marcado'),
                email_message,
                'Reserva de Salas <reservadesala@sabin.com.br>',
                to=[self.user.email, *guests],
            )

            # Form more information read https://tools.ietf.org/html/rfc5545
            vcalendar = [
                'BEGIN:VCALENDAR',
                'PRODID:-//Room Reservation//roomreservation.app//EN',
                'VERSION:2.0',
                'CALSCALE:GREGORIAN',
                'METHOD:{0}'.format('CANCEL' if self.isCanceled else 'REQUEST'),
                'BEGIN:VEVENT',
                'DTSTART:{0}'.format((self.dateInitial + timedelta(hours=3)).strftime('%Y%m%dT%H%M%SZ')),
                'DTEND:{0}'.format((self.dateFinal + timedelta(hours=3)).strftime('%Y%m%dT%H%M%SZ')),
                'DTSTAMP:{0}'.format((self.createAt + timedelta(hours=3)).strftime('%Y%m%dT%H%M%SZ')),
                'CREATED:{0}'.format((self.createAt + timedelta(hours=3)).strftime('%Y%m%dT%H%M%SZ')),
                'LAST-MODIFIED:{0}'.format((self.updateAt + timedelta(hours=3)).strftime('%Y%m%dT%H%M%SZ')),
                'ORGANIZER;CN={0}:MAILTO:{1}'.format(self.user.get_full_name(), 'reservadesalas@sabin.com.br'),
                'UID:{0}@roomreservation.app'.format(self.calendarUUID.hex.lower()),
                *['ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP='
                  'TRUE;CN={0};X-NUM-GUESTS=0:mailto:{0}'.format(g) for g in guests],
                'X-MICROSOFT-CDO-OWNERAPPTID:{0}'.format(self.calendarOwnerTID),
                'DESCRIPTION:{0}'.format(self.description),
                'LOCATION:{0}'.format(self.room.name),
                'SEQUENCE:{0}'.format('1' if self.isCanceled else '0'),
                'STATUS:{0}'.format('CANCELLED' if self.isCanceled else 'CONFIRMED'),
                'SUMMARY:{0}'.format(self.name),
                'TRANSP:OPAQUE',
                'END:VEVENT',
                'END:VCALENDAR',
            ]
            text_wrap = textwrap.TextWrapper(width=75)
            text_calendar = '\n'.join(['\n '.join(text_wrap.wrap(text=i)) for i in vcalendar])

            # first create MIMEBase, then set content-transfer-encoding, then set payload
            # don't forget add in content-type header the flag method=REQUEST
            calendar = MIMEText('text', 'calendar')
            calendar.set_payload(quopri.encodestring(bytes(text_calendar.encode('utf8'))), charset='utf-8')
            calendar.replace_header('Content-Transfer-Encoding', 'quoted-printable')
            calendar.replace_header('Content-Type', 'text/calendar; charset="utf-8"; method={0}'.format(
                'CANCEL' if self.isCanceled else 'REQUEST'))

            email.attach(calendar)
            email.attach('invite.ics', text_calendar, 'application/ics')

            email.send(fail_silently=False)
            logger.info('Email sent')
        except Exception as e:
            logger.error("Send email error", exc_info=e)

    def __notify_user_action_saved(self):
        query_set_users = Notification.objects.values('user__email').filter(action='reservation-saved')
        users = [e.get('user__email') for e in query_set_users if e.get('user__email', False)]
        if len(users) < 1:
            return

        email_message = '\n'.join([
            'Reserva Confirmada',
            '{0}: {1}'.format('Data inicial', self.dateInitial.strftime('%d/%m/%Y %H:%M')),
            '{0}: {1}'.format('Data final', self.dateFinal.strftime('%d/%m/%Y %H:%M')),
            '{0}: {1}'.format('Recursos', self.reservation_resource_list()),
            '{0}: {1}'.format('Quantidade de participantes', self.numberOfGuests),
            '{0}: {1}'.format('Público alvo', self.reservationPublic.name),
            '{0}: {1}'.format('Formato da sala', self.reservationRoomFormat.name if self.reservationRoomFormat else ''),
            '{0}: {1}'.format('Objetivo da reserva', self.reservationType.name),
            '{0}: {1}'.format('Descrição', self.description),
        ])

        try:
            send_mail(
                '{0}'.format(self.room.name),
                email_message,
                'Reserva de Salas <reservadesala@sabin.com.br>',
                users
            )
            logger.info('Notify users success')
        except Exception as e:
            logger.error('Notify users error', exc_info=e)
