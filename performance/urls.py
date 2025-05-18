from django.urls import include, path
from rest_framework import routers
from performance.views import (
    TheaterHallViewSet,
    PerformanceViewSet,
    ReservationViewSet
)

app_name = "performance"

router = routers.DefaultRouter()
router.register("theater_halls", TheaterHallViewSet, basename="theater_hall")
router.register("performances", PerformanceViewSet, basename="performance")
router.register("reservations", ReservationViewSet, basename="reservation")

urlpatterns = [path("", include(router.urls))]
