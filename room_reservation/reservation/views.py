import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET

from room_reservation.core.models import Room, RoomLink, RoomProperty, Reservation
from room_reservation.reservation.forms import BigFilterForm, ReservationForm

logger = logging.getLogger('django')


@require_GET
def logout(request):
    auth_logout(request)
    return redirect('reservation_login')


def clean_filter(request):
    big_filter = BigFilterForm(request.GET)
    if big_filter.is_valid():
        form_filter = big_filter.cleaned_data

        if str(form_filter.get('date_init')) > str(form_filter.get('date_end')) \
                or form_filter.get('date_init') == form_filter.get('date_end') \
                and form_filter.get('date_init') and form_filter.get('date_end') != "":
            messages.warning(request, _('Dates don\'t match.'))
            return redirect(reverse('reservation_index'))

        dtInitial = form_filter.get('date_init')
        dtFinal = form_filter.get('date_end')

        daysDiff = dtFinal - dtInitial

        end = timedelta(minutes=30)
        if daysDiff < end:
            messages.warning(request, _('Minimum scheduling time is 30 minutes.'))
            return redirect(reverse('reservation_index'))

        days = timedelta(days=3)
        if daysDiff > days:
            messages.warning(request, _('Scheduling period cannot be longer than 3 days.'))
            return redirect(reverse('reservation_index'))


@login_required
@require_GET
def index(request):
    room_queryset = Room.objects.all()

    form_filter = {}
    context = {
        'room_properties': RoomProperty.objects.all(),
    }
    big_filter = BigFilterForm(request.GET)
    big_filter.fields['room_property'].choices = [(rp.id, rp.name,) for rp in context['room_properties']]
    if big_filter.is_valid():
        form_filter = big_filter.cleaned_data

    if form_filter.get('number_people'):
        room_queryset = room_queryset.filter(Q(numberPeople__gte=form_filter.get('number_people')) | Q(
            numberPeopleAggregated__gte=form_filter.get('number_people')))

    if form_filter.get('room'):
        room_queryset = room_queryset.filter(name__contains=form_filter.get('room'))

    if len(form_filter.get('room_property', [])) > 0:
        room_queryset = room_queryset.filter(roomProperty__in=form_filter.get('room_property')).distinct()

    if (form_filter.get('date_init') and form_filter.get('date_end')) and form_filter.get('date_end') > form_filter.get(
            'date_init'):

        occupied = Reservation.objects.filter(
            Q(dateInitial__gte=form_filter.get('date_init')) & Q(dateFinal__lte=form_filter.get('date_end')) |
            Q(dateInitial__lte=form_filter.get('date_init')) & Q(dateFinal__gte=form_filter.get('date_end')) |
            Q(dateInitial__gte=form_filter.get('date_end')) & Q(dateFinal__lte=form_filter.get('date_init')) |
            Q(dateInitial__lt=form_filter.get('date_end')) & Q(dateFinal__gt=form_filter.get('date_init'))
        )

        if occupied and len(occupied) > 0:
            room_queryset = room_queryset.exclude(pk__in=[occ.room.id for occ in occupied])

    context['form'] = form_filter

    validate_form_filter = clean_filter(request)  # call method clean_filter in index
    if validate_form_filter:
        return render(request, 'reservation/index.html', context)

    context['rooms'] = [r for r in room_queryset if form_filter.get('number_people', 0) >= 9 or r.numberPeople < 9]
    return render(request, 'reservation/index.html', context)


@login_required
def clean_form_room(request, room):
    video_conferencing = Room.objects.get(pk=room, videoConferecingOption=True)
    form_room = ReservationForm(request.POST)
    if form_room.is_valid():
        form = form_room.cleaned_data

        if str(form.get('dateInitial')) > str(form.get('dateFinal')) \
                or form.get('dateInitial') == form.get('dateFinal') \
                and form.get('dateInitial') and form.get('dateFinal') != "":
            messages.warning(request, _('Dates don\'t match.'))
            return redirect('reservation_room_detail', room)

        initial_date = form.get('dateInitial')
        final_date = form.get('dateFinal')

        date_diff = final_date - initial_date

        end = timedelta(minutes=30)
        if date_diff < end:
            messages.warning(request, _('Minimum scheduling time is 30 minutes.'))
            return redirect('reservation_room_detail', room)

        days = timedelta(days=3)
        if date_diff > days:
            messages.warning(request, _('Scheduling period cannot be longer than 3 days.'))
            return redirect('reservation_room_detail', room)

        time_limit_schedules = timedelta(hours=4)
        if video_conferencing and time_limit_schedules < date_diff:
            messages.warning(request, _('schedules of up to 4 hours per period'))
            return redirect('reservation_room_detail', room)


@login_required
def room_detail(request, room):
    temp_data = request.session.get('temp_data', {})
    context = {
        'date_init': request.GET.get('date_init', temp_data.get('date_init')),
        'date_end': request.GET.get('date_end', temp_data.get('date_end')),
        'number_people': request.GET.get('number_people', temp_data.get('number_people')),
    }
    room_model = Room.objects.get(pk=room)

    if request.method != 'POST':
        context['room'] = room_model

        if request.session.get('tmp_form', None):
            context['form'] = ReservationForm(request.session.get('tmp_form', None))
            del request.session['tmp_form']
        else:
            context['form'] = ReservationForm()

        linked_rooms = list(RoomLink.objects.filter(room=room_model))  # return msg if there are linked rooms
        if len(linked_rooms) == 1:
            context['names_linked_rooms'] = " ".join([str(i) for i in linked_rooms])
        elif len(linked_rooms) > 1:
            context['names_linked_rooms'] = " e ".join([str(i) for i in linked_rooms])
        elif len(linked_rooms) == 1:
            context['names_linked_rooms'] = str(linked_rooms.pop())

        context['has_linked_room'] = len(linked_rooms)
        # context['form'].fields['numberOfGuests'].max_value = room_model.number_people
        context['form'].fields['dateInitial'].initial = context['date_init']
        context['form'].fields['dateFinal'].initial = context['date_end']
        context['form'].fields['numberOfGuests'].initial = context['number_people']

        return render(request, 'reservation/room.html', context)

    reservation_form = ReservationForm(request.POST)
    request.session['tmp_form'] = request.POST

    if room_model.allowRoomType:
        reservation_form.fields['reservationRoomFormat'].required = True

    if not reservation_form.is_valid():
        messages.error(request, _('Your form contains some error.'))
        return redirect('reservation_room_detail', room)

    form_data = reservation_form.cleaned_data

    occupied = Reservation.objects.filter(room=room).filter(
        Q(dateInitial__gte=form_data.get('dateInitial'), dateFinal__lte=form_data.get('dateFinal')) |
        Q(dateInitial__lte=form_data.get('dateInitial'), dateFinal__gte=form_data.get('dateFinal')) |
        Q(dateInitial__gt=form_data.get('dateFinal'), dateFinal__lt=form_data.get('dateInitial')) |
        Q(dateInitial__lt=form_data.get('dateFinal'), dateFinal__gt=form_data.get('dateInitial'))
    )

    if len(occupied) > 0:
        messages.warning(request, _('This room are reserved.'))
        return redirect('reservation_room_detail', room)

    linked_rooms = RoomLink.objects.filter(room=room_model).order_by('position')

    linked_rooms_reserved = []
    if form_data.get('numberOfGuests') > room_model.numberPeople and len(linked_rooms) > 0:
        limit_of_rooms = room_model.numberPeople
        for link in linked_rooms:
            limit_of_rooms += link.linkRoom.numberPeople
            _link_occupied = Reservation.objects.filter(room=link.linkRoom).exclude(isCanceled=True).filter(
                Q(dateInitial__gte=form_data.get('dateInitial'), dateFinal__lte=form_data.get('dateFinal')) |
                Q(dateInitial__lte=form_data.get('dateInitial'), dateFinal__gte=form_data.get('dateFinal')) |
                Q(dateInitial__gt=form_data.get('dateFinal'), dateFinal__lt=form_data.get('dateInitial')) |
                Q(dateInitial__lt=form_data.get('dateFinal'), dateFinal__gt=form_data.get('dateInitial'))
            )

            if len(_link_occupied) > 0:
                messages.warning(request, _("Room are reserved for this period."))
                return redirect('reservation_room_detail', room)
            linked_rooms_reserved.append(link.linkRoom)
            if limit_of_rooms >= form_data.get('numberOfGuests'):
                break

    elif form_data.get('numberOfGuests') > room_model.numberPeople:
        messages.warning(request, _("This room exceeded limit of people."))
        return redirect('reservation_room_detail', room)

    reservation_resources = form_data.get('reservationResource')
    del form_data['reservationResource']

    booking = Reservation(
        room=room_model,
        user=request.user,
        booked=room_model.autoReserve,
        **form_data
    )

    if clean_form_room(request, room):  # call method form_clean_room
        return redirect('reservation_room_detail', room)

    try:
        booking.save()
        if len(reservation_resources) > 0:
            booking.reservationResource.add(*reservation_resources)

        for link_room in linked_rooms_reserved:
            _booking = Reservation(
                linkedReservation=booking,
                isLinkedRoom=True,
                room=link_room,
                user=request.user,
                booked=True,
                **form_data
            )

            _booking.save()

        del request.session['tmp_form']

        messages.success(request, _('Your reservation is saved.'))
        return redirect('reservation_reservations')
    except Exception as e:
        logger.error(e)
        messages.error(request, _('Some error occurred during booking.'))
        return redirect('reservation_room_detail', room)


@login_required
@require_GET
def reservations(request):
    context = {
        'reservations': Reservation.objects.filter(user=request.user, isCanceled=False, isLinkedRoom=False).order_by(
            '-createAt')
    }
    return render(request, 'reservation/reservations.html', context)


@login_required
@require_GET
def cancel_reservation(request, reservation):
    r = Reservation.objects.get(pk=reservation, user=request.user)
    if not r:
        messages.warning(request, _('This reservation not found.'))
    try:
        r.isCanceled = True
        r.delete()
        for ch in r.linked_rooms.all():
            ch.isCanceled = True
            ch.save()
        messages.success(request, _('Reservation canceled.'))
    except Exception:
        messages.warning(request, _('Reservation not canceled.'))

    return redirect('reservation_reservations')
