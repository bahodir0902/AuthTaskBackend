from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

from apps.users.service import send_activation_invite
from .models import User, UserProfile


class UserAdminForm(forms.ModelForm):
    let_user_set_password = forms.BooleanField(
        label=_("Let user set password"),
        required=False,
        initial=True,
        help_text=_(
            "If checked, an invitation link will be sent to the user. If unchecked, you can set a password manually."),
        widget=forms.CheckboxInput(attrs={'class': 'user-password-toggle'})
    )

    raw_password = forms.CharField(
        label=_("Set password"),
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'vTextField password-field',
            'placeholder': _('Enter password for the user'),
            'autocomplete': 'new-password'
        }),
        help_text=_("Enter a raw password. Django will automatically hash it before saving.")
    )

    class Meta:
        model = User
        fields = "__all__"
        exclude = ("password",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['let_user_set_password'].widget = forms.HiddenInput()
            self.fields['raw_password'].widget = forms.HiddenInput()
            self.fields['let_user_set_password'].required = False
            self.fields['raw_password'].required = False

    def clean(self):
        cleaned_data = super().clean()

        if not self.instance.pk:
            let_user_set = cleaned_data.get('let_user_set_password', True)
            raw_password = cleaned_data.get('raw_password')

            if not let_user_set and not raw_password:
                raise ValidationError({
                    'raw_password': _("Please enter a password or check 'Let user set password'.")
                })

            if let_user_set and raw_password:
                raise ValidationError(
                    _("You cannot set both 'Let user set password' and provide a manual password. Please choose one option.")
                )

        return cleaned_data

    def save(self, commit=True):
        user: User = super().save(commit=False)

        is_new_user = not self.instance.pk

        if is_new_user:
            let_user_set = self.cleaned_data.get('let_user_set_password', True)
            raw_password = self.cleaned_data.get('raw_password')

            if let_user_set:
                user.set_unusable_password()
                user.save()

                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                send_activation_invite(user.email, user.first_name, uid, token)
            else:
                user.password = make_password(raw_password)
                user.must_set_password = False
                user.email_verified = True
                user.save()

        if commit:
            if not is_new_user:
                user.save()
            self.save_m2m()

        return user


    class Media:
        css = {
            'all': ('admin/css/user_admin_custom.css',)
        }
        js = ('admin/js/user_admin_custom.js',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm

    fieldsets = (
        (_("Personal Info"), {
            "fields": ("first_name", "middle_name", "last_name", "email"),
            "description": _("Basic information about the user.")
        }),
        (_("Password Settings"), {
            "fields": ("let_user_set_password", "raw_password"),
            "description": format_html(
                '<div class="password-info">'
                '<strong>⚠️ Password Configuration (New Users Only)</strong><br>'
                '• <strong>Let user set password (checked):</strong> User will receive an invitation email to set their own password.<br>'
                '• <strong>Let user set password (unchecked):</strong> You can set a password manually below. Django will hash it automatically.'
                '</div>'
            ),
            "classes": ("password-settings",),
        }),
        (_("Status & Access"), {
            "fields": (
                "role",
                "is_active",
                "email_verified",
                "must_set_password",
                "mfa_enabled",
            ),
            "classes": ("collapse",),
            "description": _("Control user's access level and account status.")
        }),
        (_("Permissions"), {
            "fields": (
                "groups",
                "user_permissions",
            ),
            "classes": ("collapse",),
            "description": _("Assign roles, groups, and specific permissions to this user."),
        }),
        (_("Important Dates"), {
            "fields": ("last_login", "date_joined"),
            "classes": ("collapse",)
        }),
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