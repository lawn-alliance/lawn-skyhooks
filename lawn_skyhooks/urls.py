"""Routes."""

# Django
from django.urls import path

from . import views

app_name: str = "lawn_skyhooks"

urlpatterns = [
    path("", views.index, name="index"),
    path("empty/<int:pk>", views.empty_skyhook, name="empty_skyhook"),
]
