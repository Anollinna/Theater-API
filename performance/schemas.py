from drf_spectacular.utils import extend_schema, OpenApiParameter


theater_hall_schema = {
    'list': extend_schema(summary="List all theater halls"),
    'create': extend_schema(summary="Create a new theater hall"),
}

performance_schema = {
    'list': extend_schema(
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
    'retrieve': extend_schema(summary="Get performance details"),
    'create': extend_schema(summary="Create a new performance"),
    'update': extend_schema(summary="Update a performance"),
    'partial_update': extend_schema(summary="Partially update a performance"),
    'destroy': extend_schema(summary="Delete a performance"),
}

reservation_schema = {
    'list': extend_schema(summary="List current user`s reservations"),
    'create': extend_schema(
        summary="Create a reservation with tickets",
        request='ReservationSerializer',
        responses={201: 'ReservationSerializer'}
    ),
}
