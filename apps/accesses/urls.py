from django.urls import include, path
from rest_framework import routers

from .views import AccessRuleViewSet, ResourceViewSet

router = routers.DefaultRouter()
router.register("resource", ResourceViewSet)
router.register("access-rule", AccessRuleViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
