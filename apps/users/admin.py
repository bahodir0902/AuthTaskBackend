from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.users.service import send_activation_invite
from .models import User, UserProfile


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"
        exclude = ("password",)

    def save(self, commit=True):
        user: User = super().save(commit=False)
        if not user.pk:
            user.set_unusable_password()
            user.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            send_activation_invite(user.email, user.first_name, uid, token)

        if commit:
            user.save()
            self.save_m2m()
        return user


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm

    fieldsets = (
        (_("Personal Info"), {"fields": ("first_name", "middle_name", "last_name", "email")}),
        (_("Status & Access"), {
            "fields": (
                "role",
                "is_active",
                "email_verified",
                "must_set_password",
                "mfa_enabled",
            ),
            "classes": ("collapse",),
        }),
        (_("Permissions"), {
            "fields": (
                "groups",
                "user_permissions",
            ),
            "classes": ("collapse",),
            "description": _("Assign roles, groups, and specific permissions to this user."),
        }),
        (_("Important Dates"), {"fields": ("last_login", "date_joined")}),
    )

    readonly_fields = ("last_login", "date_joined")

    list_display = (
        "colored_name",
        "email",
        "role_badge",
        "email_verified_icon",
        "is_active_icon",
        "mfa_icon",
        "date_joined",
    )
    list_filter = (
        "role",
        "is_active",
        "email_verified",
        "must_set_password",
        "mfa_enabled",
        "groups",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)
    list_per_page = 25
    list_display_links = ("colored_name", "email")

    def email_verified_icon(self, obj):
        color = "green" if obj.email_verified else "red"
        icon = "✔️" if obj.email_verified else "❌"
        return format_html('<span style="color:{};">{}</span>', color, icon)
    email_verified_icon.short_description = "Email Verified"

    def is_active_icon(self, obj):
        color = "green" if obj.is_active else "gray"
        icon = "🟢" if obj.is_active else "⚪"
        return format_html('<span style="color:{};">{}</span>', color, icon)
    is_active_icon.short_description = "Active"

    def mfa_icon(self, obj):
        return format_html("🔒" if obj.mfa_enabled else "—")
    mfa_icon.short_description = "MFA"

    def role_badge(self, obj):
        colors = {
            "admin": "#007bff",
            "manager": "#ff9800",
            "user": "#4caf50",
            "guest": "#9e9e9e",
        }
        color = colors.get(obj.role, "#999")
        return format_html(
            '<span style="background-color:{}; color:white; padding:2px 8px; border-radius:10px; font-size:0.85em;">{}</span>',
            color,
            obj.get_role_display(),
        )
    role_badge.short_description = "Role"

    def colored_name(self, obj):
        full_name = f"{obj.first_name or ''} {obj.last_name or ''}".strip() or "—"
        color = "#007bff" if obj.role == "admin" else "#333"
        return format_html(f'<b style="color:{color};">{full_name}</b>')
    colored_name.short_description = "Name"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass