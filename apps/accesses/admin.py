from django.contrib import admin
from .models import Resource, AccessRule

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    pass

@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):
    pass