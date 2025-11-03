from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ActivateAccountView, AuthViewSet, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("auth", AuthViewSet, basename="auth")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/activate/", ActivateAccountView.as_view(), name="activate-account"),
]
