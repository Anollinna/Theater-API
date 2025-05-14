from django.db import models
from theater.models import Play
from django.conf import settings


class TheaterHall(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self):
        return self.name


class Performance(models.Model):
    show_time = models.DateTimeField()
    play = models.ForeignKey(Play, on_delete=models.CASCADE, related_name="performances")
    theater_hall = models.ForeignKey(TheaterHall, on_delete=models.CASCADE, related_name="performances")

    @property
    def tickets_available(self):
        hall_capacity = self.theater_hall.rows * self.theater_hall.seats_in_row
        sold_tickets = self.tickets.count()
        return hall_capacity - sold_tickets

    def __str__(self):
        return f"{self.play.title} at {self.show_time}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE, related_name="tickets")
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="tickets")

    def __str__(self):
        return str(
            f"{self.performance} (row: {self.row}, seat: {self.seat})"
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["performance", "row", "seat"],
                name="unique_ticket_per_seat",
            )
        ]
        ordering = ["row", "seat"]
