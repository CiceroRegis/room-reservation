from django.urls import path
from django.contrib.auth import views as auth_views

from room_reservation.reservation import views
from room_reservation.reservation.views import *

urlpatterns = [
    path('', index, name='reservation_index'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='reservation_login'),
    path('accounts/logout/', logout, name='reservation_logout'),
    path('room/<int:room>', room_detail, name='reservation_room_detail'),
    path('reservations', reservations, name='reservation_reservations'),
    path('reservation/<int:reservation>/cancel', cancel_reservation, name='reservation_cancel'),
]
