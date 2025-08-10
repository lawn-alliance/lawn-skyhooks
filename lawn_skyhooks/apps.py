# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# AA Base Plugin
from lawn_skyhooks import __version__


class ExampleConfig(AppConfig):
    name = "lawn_skyhooks"
    label = "lawn_skyhooks"
    verbose_name = _(f"LAWN Skyhooks v{__version__}")
