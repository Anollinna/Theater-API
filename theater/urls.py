from django.urls import path, include
from rest_framework import routers
from theater.views import (
    GenreViewSet,
    ActorViewSet,
    PlayViewSet
)

app_name = "theater"

router = routers.DefaultRouter()
router.register("genres", GenreViewSet)
router.register("actors", ActorViewSet)
router.register("plays", PlayViewSet, basename="play")

urlpatterns = [
    path("", include(router.urls)),
]
