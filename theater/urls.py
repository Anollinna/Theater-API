from django.urls import path, include
from rest_framework import routers
from theater.views import (
    GenreViewSet,
    ActorViewSet,
    PlayViewSet
)

app_name = "theater"

router = routers.DefaultRouter()
router.register("genres", GenreViewSet, basename="genre")
router.register("actors", ActorViewSet, basename="actor")
router.register("plays", PlayViewSet, basename="play")

urlpatterns = [
    path("", include(router.urls)),
]
