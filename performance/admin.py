from django.contrib import admin
from .models import (
    TheaterHall,
    Performance,
    Ticket,
    Reservation
)

admin.site.register(TheaterHall)
admin.site.register(Performance)
admin.site.register(Ticket)
admin.site.register(Reservation)
