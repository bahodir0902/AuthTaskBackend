from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from apps.common.permissions import IsAdminRole

from .models import AccessRule, Resource
from .serializers import AccessRuleSerializer, ResourceSerializer


@extend_schema(tags=["Resources"])
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAdminRole]


@extend_schema(tags=["Accesses"])
class AccessRuleViewSet(viewsets.ModelViewSet):
    queryset = AccessRule.objects.select_related("resource").all()
    serializer_class = AccessRuleSerializer
    permission_classes = [IsAdminRole]
