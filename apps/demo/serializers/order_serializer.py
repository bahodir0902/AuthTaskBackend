from rest_framework import serializers

from apps.demo.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user", "title", "description", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
