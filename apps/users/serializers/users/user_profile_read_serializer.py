from rest_framework import serializers

from apps.users.models import UserProfile

from .user_serializer import UserSerializer


class UserProfileReadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "birth_date",
            "phone_number",
            "profile_photo",
            "updated_at",
        ]
