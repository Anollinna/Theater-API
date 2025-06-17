from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import ValidationError
from rest_framework import mixins
from drf_spectacular.utils import extend_schema_view, extend_schema

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
from theater.schemas import (
    genre_schema,
    actor_schema,
    play_schema,
    upload_image_schema
)


@extend_schema_view(**genre_schema)
class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)


@extend_schema_view(**actor_schema)
class ActorViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsAdminOrReadOnly,)


@extend_schema_view(**play_schema)
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

    @upload_image_schema
    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        play = self.get_object()
        serializer = self.get_serializer(play, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
