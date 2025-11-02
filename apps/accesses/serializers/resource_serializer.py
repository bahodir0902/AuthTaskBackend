from rest_framework import serializers

from apps.accesses.models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "code", "name", "description"]
