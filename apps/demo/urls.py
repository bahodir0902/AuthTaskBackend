from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrdersViewSet

router = DefaultRouter()
router.register("orders", OrdersViewSet)
urlpatterns = [
    path("", include(router.urls)),
]
