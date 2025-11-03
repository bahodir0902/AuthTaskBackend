from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accesses.models import AccessRule, Resource
from apps.accesses.permissions import HasResourcePermission
from apps.users.models.user import Role

from .models import Order
from .serializers import OrderSerializer


@extend_schema(tags=["Orders"])
class OrdersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasResourcePermission]
    access_resource = "orders"
    queryset = Order.objects.select_related("user").all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == Role.ADMIN:
            return qs

        resource = Resource.objects.filter(code=self.access_resource).first()
        rule = (
            AccessRule.objects.filter(role=user.role, resource=resource).first()
            if resource
            else None
        )

        if rule and rule.read_all:
            return qs
        if rule and rule.read_own:
            return qs.filter(user=user)

        return qs.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
