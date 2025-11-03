from rest_framework.permissions import BasePermission

from apps.users.models.user import Role as UserRole

from .models import AccessRule, Resource

ACTION_MAP = {
    "list": ("read_all", "read_own"),
    "retrieve": ("read_all", "read_own"),
    "create": ("create", None),
    "update": ("update_all", "update_own"),
    "partial_update": ("update_all", "update_own"),
    "destroy": ("delete_all", "delete_own"),
    "GET": ("read_all", "read_own"),
    "POST": ("create", None),
    "PUT": ("update_all", "update_own"),
    "PATCH": ("update_all", "update_own"),
    "DELETE": ("delete_all", "delete_own"),
}


class HasResourcePermission(BasePermission):
    def _get_rule(self, user, res_code):
        try:
            resource = Resource.objects.get(code=res_code)
            return AccessRule.objects.get(role=user.role, resource=resource)
        except (Resource.DoesNotExist, AccessRule.DoesNotExist):
            return None

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False
        if request.user.role == UserRole.ADMIN:
            return True

        res_code = getattr(view, "access_resource", None)
        if not res_code:
            return False

        action = getattr(view, "action", None) or request.method
        need_all, need_own = ACTION_MAP.get(action, (None, None))
        if not (need_all or need_own):
            return False

        rule = self._get_rule(request.user, res_code)

        if not rule:
            return False

        if need_all and getattr(rule, need_all, False):
            return True

        if need_own and getattr(rule, need_own, False):
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.ADMIN:
            return True

        res_code = getattr(view, "access_resource", None)
        if not res_code:
            return False

        action = getattr(view, "action", None) or request.method
        need_all, need_own = ACTION_MAP.get(action, (None, None))
        if not (need_all or need_own):
            return False

        rule = self._get_rule(request.user, res_code)
        if not rule:
            return False

        if need_all and getattr(rule, need_all, False):
            return True

        if need_own and getattr(rule, need_own, False):
            owner_field = getattr(view, "owner_field", "user")
            owner = getattr(obj, owner_field, None)
            owner_id = getattr(owner, "id", owner)
            return owner_id == request.user.id

        return False
