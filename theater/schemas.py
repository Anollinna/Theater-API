from drf_spectacular.utils import extend_schema, OpenApiParameter

genre_schema = {
    "list": extend_schema(summary="List all genres"),
    "create": extend_schema(summary="Create a new genre"),
}

actor_schema = {
    'list': extend_schema(summary="List all actors"),
    'create': extend_schema(summary="Create a new actor"),
}

play_schema = {
    'list': extend_schema(
        summary="List all plays with filters",
        parameters=[
            OpenApiParameter(
                name="genres",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by genre IDs (e.g., ?genres=1,2)"
            ),
            OpenApiParameter(
                name="actors",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by actor IDs (e.g., ?actors=3,4)"
            ),
            OpenApiParameter(
                name="title",
                type=str,
                description="Filter by partial title (e.g., ?title=king)",
                required=False
            ),
        ]
    ),
    'retrieve': extend_schema(summary="Retrieve play details"),
    'create': extend_schema(summary="Create a new play"),
}

upload_image_schema = extend_schema(
    summary="Upload an image for the play",
    request='PlayImageSerializer',
    responses={200: 'PlayImageSerializer'}
)
