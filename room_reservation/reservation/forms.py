from django import forms
from room_reservation.core.models import Reservation, ReservationResource


class BigFilterForm(forms.Form):
    room = forms.CharField(required=False)
    number_people = forms.IntegerField(required=True, min_value=2)
    room_type = forms.MultipleChoiceField(required=False)
    date_init = forms.DateTimeField(required=True)
    date_end = forms.DateTimeField(required=True)
    room_property = forms.MultipleChoiceField(required=False)


class ReservationForm(forms.ModelForm):
    reservationResource = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False,
        queryset=ReservationResource.objects.all()
    )

    class Meta:
        model = Reservation
        exclude = ('room', 'user', 'booked', 'updateAt', 'createAt',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dateInitial'].widget.attrs.update({
            'autocomplete': 'off',
            'placeholder': 'Data Inicial',
            'class': 'form-control datetimepicker'})
        self.fields['dateFinal'].widget.attrs.update({
            'autocomplete': 'off',
            'placeholder': 'Data final',
            'class': 'form-control datetimepicker'})

        self.fields['name'].widget.attrs.update({'placeholder': 'Nome do evento', 'class': 'form-control'})
        self.fields['reservationType'].widget.attrs.update({'class': 'form-control'})
        self.fields['reservationPublic'].widget.attrs.update({'class': 'form-control'})
        self.fields['numberOfGuests'].widget.attrs.update({'min': 1, 'class': 'form-control'})
        self.fields['reservationRoomFormat'].widget.attrs.update({'class': 'form-control'})
        self.fields['guests'].widget.attrs.update({'id': 'id_guests', 'style': 'display: none;'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Observação','class':'form-control' })
