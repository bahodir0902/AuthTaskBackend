from django.urls import include, path

urlpatterns = [
    path("accounts/", include("apps.users.urls")),
    path("access/", include("apps.accesses.urls")),
    path("demo/", include("apps.demo.urls")),
]
