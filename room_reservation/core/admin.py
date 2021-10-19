from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from room_reservation.core.models import *
from room_reservation.core.forms import *

admin.site.register(User, UserAdmin)


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(RoomProperty)
class RoomPropertyAdmin(admin.ModelAdmin):
    pass


class RoomImageInlineForm(admin.StackedInline):
    model = RoomImage
    extra = 1


class RoomLinkInlineForm(admin.TabularInline):
    model = RoomLink
    form = RoomLinkForm
    fk_name = 'room'
    extra = 1

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    filter_horizontal = ('roomProperty', 'linkRoom',)
    form = RoomAdminForm
    inlines = (RoomLinkInlineForm, RoomImageInlineForm,)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'room', 'user', 'name', 'numberOfGuests', 'reservationPublic', 'reservationRoomFormat', 'date_initial',
        'date_final', 'booked')

    list_filter = ('dateInitial', 'room')
    search_fields = (
        'room__name', 'user__username', 'numberOfGuests',
        'dateInitial', 'dateFinal'
    )
    readonly_fields = (
        'room', 'reservationType', 'reservationPublic', 'user', 'name', 'numberOfGuests',
        'reservationPublic', 'reservationRoomFormat', 'dateInitial',
        'dateFinal', 'description', 'guests',)

    list_per_page = 10
    date_hierarchy = 'dateInitial'

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.filter(isLinkedRoom=False)


@admin.register(ReservationType)
class ReservationTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(ReservationPublic)
class ReservationPublicAdmin(admin.ModelAdmin):
    pass


@admin.register(ReservationRoomFormat)
class ReservationRoomFormatAdmin(admin.ModelAdmin):
    pass


@admin.register(ReservationResource)
class ReservationResourceAdmin(admin.ModelAdmin):
    pass
