from datetime import datetime
from theater_api.permissions import IsAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet
from django.db.models import F, Count
from performance.models import (
    TheaterHall,
    Performance,
    Reservation
)
from performance.serializers import (
    TheaterHallSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
    ReservationSerializer,
    ReservationListSerializer, TicketSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="List all theater halls"),
    create=extend_schema(summary="Create a new theater hall"),
)
class TheaterHallViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = TheaterHall.objects.all()
    serializer_class = TheaterHallSerializer
    permission_classes = (IsAdminOrReadOnly, )


@extend_schema_view(
    list=extend_schema(
        summary="List all performances",
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                description="Filter by date (YYYY-MM-DD)",
                required=False,
            ),
            OpenApiParameter(
                name="play",
                type=str,
                description="Filter by play ID",
                required=False,
            ),
        ]
    ),
    retrieve=extend_schema(summary="Get performance details"),
    create=extend_schema(summary="Create a new performance"),
    update=extend_schema(summary="Update a performance"),
    partial_update=extend_schema(summary="Partially update a performance"),
    destroy=extend_schema(summary="Delete a performance"),
)
class PerformanceViewSet(viewsets.ModelViewSet):
    serializer_class = PerformanceSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def get_queryset(self):
        queryset = (
            Performance.objects.select_related("play", "theater_hall")
            .annotate(
                available_tickets=(
                        F("theater_hall__rows")
                        * F("theater_hall__seats_in_row")
                        - Count("tickets")
                )
            )
        )
        date = self.request.query_params.get("date")
        play_id_str = self.request.query_params.get("play")

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)

        if play_id_str and play_id_str.isdigit():
            queryset = queryset.filter(play_id=int(play_id_str))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer

        if self.action == "retrieve":
            return PerformanceDetailSerializer

        return PerformanceSerializer


@extend_schema_view(
    list=extend_schema(summary="List current user`s reservations"),
    create=extend_schema(
        summary="Create a reservation with tickets",
        request=ReservationSerializer,
        responses={201: ReservationSerializer}
    ),
)
class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).prefetch_related(
        "tickets__performance__play",
        "tickets__performance__theater_hall",
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
