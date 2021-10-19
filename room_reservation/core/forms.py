from django import forms
from room_reservation.core.models import Room, RoomLink


class RoomLinkForm(forms.ModelForm):
    class Meta:
        model = RoomLink
        exclude = ('createAt',)

    def __init__(self, *args, **kwargs):
        super(RoomLinkForm, self).__init__(*args, **kwargs)
        # if kwargs.get('instance', None):
        #     self.fields['linkRoom'].queryset = Room.objects.exclude(pk=kwargs['instance'].pk)


class RoomAdminForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ('updateAt', 'createAt',)

    # def __init__(self, *args, **kwargs):
    #     super(RoomAdminForm, self).__init__(*args, **kwargs)
    #     if kwargs.get('instance', None):
    #         self.fields['linkRoom'].queryset = Room.objects.exclude(pk=kwargs['instance'].pk)
