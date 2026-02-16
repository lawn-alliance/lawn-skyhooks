"""Routes."""

# Django
from django.urls import path

from . import __app_name__, views

app_name: str = __app_name__  # pylint: disable=invalid-name

urlpatterns = [
    path("", views.index, name="index"),
    path("empty/<int:pk>", views.empty_skyhook, name="empty_skyhook"),
    path("claim/<int:pk>", views.claim_skyhook, name="claim_skyhook"),
    path("import", views.import_data, name="import_data"),
]
