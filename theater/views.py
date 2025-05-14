from rest_framework.exceptions import ValidationError
from rest_framework import mixins
from drf_spectacular.utils import extend_schema, OpenApiParameter
from theater_api.permissions import IsAdminOrReadOnly
from rest_framework.viewsets import GenericViewSet
from theater.models import Genre, Actor, Play
from theater.serializers import (
    GenreSerializer,
    ActorSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    PlayImageSerializer
)


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)


class ActorViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsAdminOrReadOnly,)


class PlayViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = PlaySerializer
    permission_classes = (IsAdminOrReadOnly,)

    @staticmethod
    def _param_to_ints(qs):
        try:
            return [int(str_id) for str_id in qs.split(",")]
        except ValueError:
            raise ValidationError(
                "Query parameters must be integers."
            )

    def get_queryset(self):
        queryset = Play.objects.prefetch_related("genres", "actors")
        title = self.request.query_params.get("title")
        genres = self.request.query_params.get("genres")
        actors = self.request.query_params.get("actors")

        if title:
            queryset = queryset.filter(title__icontains=title)

        if genres:
            genres_ids = self._param_to_ints(genres)
            queryset = queryset.filter(genres__id__in=genres_ids)

        if actors:
            actors_ids = self._param_to_ints(actors)
            queryset = queryset.filter(actors__id__in=actors_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        if self.action == "retrieve":
            return PlayDetailSerializer

        if self.action == "upload_image":
            return PlayImageSerializer

        return PlaySerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="genres",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by Genres id (ex. ?genres=2,3)",
            ),
            OpenApiParameter(
                name="actors",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by Actors id (ex. ?actors=2,3)",
            ),
            OpenApiParameter(
                name="title",
                type=str,
                description="Filter by play, partial (ex. ?title=nbrea)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """List all plays with optional filters by title, genres, and actors."""
        return super().list(request, *args, **kwargs)
