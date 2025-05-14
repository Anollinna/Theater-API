from django.urls import include, path
from rest_framework import routers
from performance.views import (
    TheaterHallViewSet,
    PerformanceViewSet,
    ReservationViewSet
)


router = routers.DefaultRouter()
router.register("theater_halls", TheaterHallViewSet)
router.register("performances", PerformanceViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "performance"
