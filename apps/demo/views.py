from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accesses.models import Resource
from apps.accesses.permissions import HasResourcePermission
from apps.accesses.serializers import ResourceSerializer

MOCK_ORDERS = [
    {"id": 1, "owner_id": 1, "title": "Order A"},
    {"id": 2, "owner_id": 6, "title": "Order B"},
    {"id": 3, "owner_id": 7, "title": "Order C"},
    {"id": 4, "owner_id": 8, "title": "Order D"},
    {"id": 5, "owner_id": 9, "title": "Order E"},
    {"id": 6, "owner_id": 10, "title": "Order F"},
]


class OrdersViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, HasResourcePermission]
    access_resource = "orders"
    owner_field = "owner_id"  # because mock dicts, owner is just an int
    queryset = Resource.objects.none()
    serializer_class = ResourceSerializer

    def list(self, request, *args, **kwargs):
        # if user has read_all → return all, else filter by owner
        # HasResourcePermission will have already checked rule.read_all; if not allowed,
        # it still allows read_own and we filter here:
        show_all = request.user.role == "admin"  # extra fast path
        if not show_all:
            # naive: check rule; or just filter to own by default
            data = [o for o in MOCK_ORDERS if o["owner_id"] == request.user.id]
        else:
            data = MOCK_ORDERS
        return Response(data)

    def retrieve(self, request, *args, pk=None, **kwargs):
        obj = next((o for o in MOCK_ORDERS if o["id"] == int(pk)), None)
        if not obj:
            return Response({"detail": "Not found."}, status=404)
        # trigger object permission check
        self.check_object_permissions(request, obj)
        return Response(obj)

    def create(self, request, *args, **kwargs):
        # HasResourcePermission already checked rule.create
        new = {
            "id": max(o["id"] for o in MOCK_ORDERS) + 1,
            "owner_id": request.user.id,
            "title": request.data.get("title"),
        }
        MOCK_ORDERS.append(new)
        return Response(new, status=status.HTTP_201_CREATED)
