from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accesses.models import AccessRule, Resource
from apps.accesses.permissions import HasResourcePermission
from apps.users.models.user import Role

from .models import Order
from .serializers import OrderSerializer


@extend_schema(tags=["Orders"])
class OrdersViewSet(viewsets.ModelViewSet):
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

    def get_permissions(self):
        if self.action == "my_orders":
            return [IsAuthenticated()]
        return [IsAuthenticated(), HasResourcePermission()]

    @action(methods=["get"], detail=False, url_path="my-orders")
    def my_orders(self, request):
        qs = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
