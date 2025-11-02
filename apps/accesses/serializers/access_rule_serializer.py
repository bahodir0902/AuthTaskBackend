from rest_framework import serializers

from apps.accesses.models import AccessRule, Resource


class AccessRuleSerializer(serializers.ModelSerializer):
    from .resource_serializer import ResourceSerializer

    resource = ResourceSerializer(read_only=True)
    resource_id = serializers.PrimaryKeyRelatedField(
        queryset=Resource.objects.all(), write_only=True, source="resource"
    )

    class Meta:
        model = AccessRule
        fields = [
            "id",
            "role",
            "resource",
            "resource_id",
            "read_own",
            "read_all",
            "create",
            "update_own",
            "update_all",
            "delete_own",
            "delete_all",
        ]
