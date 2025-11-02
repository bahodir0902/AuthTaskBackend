from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.users.models import UserProfile


class UserProfileWriteSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    middle_name = serializers.CharField(source="user.middle_name", required=False)
    mfa_enabled = serializers.BooleanField(source="user.mfa_enabled", required=False, default=False)

    class Meta:
        model = UserProfile
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "mfa_enabled",
            "birth_date",
            "phone_number",
            "profile_photo",
            "updated_at",
        ]
        read_only_fields = ("updated_at",)
        extra_kwargs = {
            "birth_date": {"required": False},
            "middle_name": {"required": False},
            "profile_photo": {"required": False},
        }

    def validate(self, attrs):
        user_data = attrs.get("user", {})
        if "email" in user_data:
            raise ValidationError("Use the email change flow to update your email address.")
        return attrs

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if user_data:
            changed = False
            for attr in ("first_name", "last_name", "middle_name", "mfa_enabled"):
                if attr in user_data:
                    setattr(instance.user, attr, user_data[attr])
                    changed = True
            if changed:
                instance.user.save()

        return instance
