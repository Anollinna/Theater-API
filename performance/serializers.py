from rest_framework import serializers
from performance.models import (
    TheaterHall,
    Performance,
    Reservation,
    Ticket
)
from django.db import transaction
from theater.serializers import PlaySerializer


class TheaterHallSerializer(serializers.ModelSerializer):
    capacity = serializers.SerializerMethodField()

    class Meta:
        model = TheaterHall
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity"
        )

    def get_capacity(self, obj):
        return obj.rows * obj.seats_in_row


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = (
            "id",
            "show_time",
            "play",
            "theater_hall",
        )


class PerformanceListSerializer(serializers.ModelSerializer):
    play_title = serializers.CharField(source="play.title", read_only=True)
    play_image = serializers.ImageField(source="play.image", read_only=True)
    theater_hall_name = serializers.CharField(
        source="theater_hall.name",
        read_only=True
    )
    tickets_available = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = Performance
        fields = (
            "id",
            "show_time",
            "play_title",
            "play_image",
            "theater_hall_name",
            "tickets_available"
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        performance = attrs["performance"]
        row = attrs["row"]
        seat = attrs["seat"]

        max_row = performance.theater_hall.rows
        max_seat = performance.theater_hall.seats_in_row

        if row < 1 or row > max_row:
            raise serializers.ValidationError(
                {"row": f"Row must be between 1 and {max_row}."}
            )
        if seat < 1 or seat > max_seat:
            raise serializers.ValidationError(
                {"seat": f"Seat must be between 1 and {max_seat}."}
            )

        if Ticket.objects.filter(performance=performance, row=row, seat=seat).exists():
            raise serializers.ValidationError(
                "This seat is already taken fr the selected performance."
            )
        return attrs

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "performance"
        )


class TicketListSerializer(serializers.ModelSerializer):
    performance = PerformanceListSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "performance"
        )


class TicketSeatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "row",
            "seat"
        )


class PerformanceDetailSerializer(serializers.ModelSerializer):
    play = PlaySerializer(many=False, read_only=True)
    theater_hall = TheaterHallSerializer(many=False, read_only=True)
    taken_places = TicketSeatsSerializer(
        source="tickets",
        many=True,
        read_only=True
    )

    class Meta:
        model = Performance
        fields = (
            "id",
            "show_time",
            "play",
            "theater_hall",
            "taken_places"
        )


class ReservationSerializer(serializers.ModelSerializer):
    ticket = TicketSerializer(write_only=True)

    class Meta:
        model = Reservation
        fields = (
            "id",
            "created_at",
            "ticket"
        )

    def validate_tickets(self, tickets):
        if not tickets:
            raise serializers.ValidationError(
                "At least one ticket is required"
            )
        return tickets

    def create(self, validated_data):
        ticket_date = validated_data.pop("ticket")
        user = self.context["request"].user

        with transaction.atomic():
            reservation = Reservation.objects.create(user=user)
            Ticket.objects.create(reservation=reservation, **ticket_date)
            return reservation


class ReservationListSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = (
            "id",
            "created_at",
            "tickets"
        )
