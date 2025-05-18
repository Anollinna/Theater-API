from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from performance.models import (
    Reservation,
    Performance,
    TheaterHall, Ticket
)
from theater.models import Play

THEATER_HALL_URL =reverse("performance:theater_hall-list")
PERFORMANCE_URL = reverse("performance:performance-list")
RESERVATION_URL = reverse("performance:reservation-list")

User = get_user_model()


class TheaterHallViewSetTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin@test.com", password="adminpass"
        )
        self.user = User.objects.create_user(
            email="user@test.com", password="userpass"
        )

    def test_list_theater_halls(self):
        TheaterHall.objects.create(name="Main Hall", rows=10, seats_in_row=20)
        TheaterHall.objects.create(name="Small Hall", rows=5, seats_in_row=10)

        response = self.client.get(THEATER_HALL_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_admin_can_create_theater_hall(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "name": "New Hall",
            "rows": 8,
            "seats_in_row": 12
        }

        response = self.client.post(THEATER_HALL_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TheaterHall.objects.filter(name="New Hall").exists())

    def test_user_cannot_create_theater_hall(self):
        self.client.force_authenticate(user=self.user)
        payload = {"name": "Forbidden Hall", "rows": 3, "seats_in_row": 3}

        response = self.client.post(THEATER_HALL_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PerformanceViewSetTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin@test.com", password="adminpass"
        )
        self.hall = TheaterHall.objects.create(name="Stage 1", rows=10, seats_in_row=10)
        self.play = Play.objects.create(title="Hamlet", description="Drama")
        self.performance = Performance.objects.create(
            play=self.play,
            theater_hall=self.hall,
            show_time=timezone.now()
        )

    def test_list_performances(self):
        response = self.client.get(PERFORMANCE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_filter_performance_by_date(self):
        date = self.performance.show_time.date().strftime("%Y-%m-%d")

        response = self.client.get(PERFORMANCE_URL, {"date": date})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(item["show_time"].startswith(date) for item in response.data["results"])
        )

    def test_admin_can_create_performance(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "play": self.play.id,
            "theater_hall": self.hall.id,
            "show_time": timezone.now().isoformat()
        }

        response = self.client.post(PERFORMANCE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ReservationViewSetTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@test.com", password="userpass")
        self.client.force_authenticate(user=self.user)

        self.hall = TheaterHall.objects.create(name="Main Hall", rows=5, seats_in_row=5)
        self.play = Play.objects.create(title="Macbeth", description="Tragedy")
        self.performance = Performance.objects.create(
            play=self.play,
            theater_hall=self.hall,
            show_time="2030-01-01T19:00:00Z"
        )

    def test_user_can_create_reservation(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "tickets": [
                {"performance": self.performance.id, "row": 1, "seat": 1},
                {"performance": self.performance.id, "row": 1, "seat": 2},
            ]
        }

        response = self.client.post(RESERVATION_URL, data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 2)

        reservation = Reservation.objects.first()
        self.assertEqual(reservation.tickets.count(), 2)

    def test_user_can_list_reservations(self):
        reservation = Reservation.objects.create(user=self.user)
        reservation.tickets.create(performance=self.performance, row=1, seat=1)

        response = self.client.get(RESERVATION_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
