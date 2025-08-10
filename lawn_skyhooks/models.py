"""Models."""

# Django
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Alliance Auth
from allianceauth.framework.api.user import get_sentinel_user


class LawnSkyhooks(models.Model):
    """A meta model for app permissions."""

    class Meta:
        """Meta definitions."""

        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"),)


class Skyhook(models.Model):
    """A Skyhook is a location where resources accumulate."""

    # Define allowed choices for resource type
    RESOURCE_TYPE_CHOICES = [
        ("magmatic gas", "Magmatic Gas"),
        ("superionic ice", "Superionic Ice"),
    ]

    # Each location should be unique
    location = models.CharField(
        max_length=255,
        unique=True,  # ensures uniqueness
        help_text="Name or system of the Skyhook's location.",
    )

    resource_type = models.CharField(
        max_length=50,
        choices=RESOURCE_TYPE_CHOICES,
        help_text="Type of resource this Skyhook accumulates.",
    )

    resource_per_minute = models.FloatField(
        default=0.0, help_text="Accumulation rate of the resource per minute."
    )

    last_emptied_at = models.DateTimeField(
        null=True, blank=True, help_text="Timestamp when this Skyhook was last emptied."
    )

    def estimate_current_quantity(self):
        """
        Calculates how much resource has accumulated
        since the last time it was emptied.
        """
        # Django

        if self.last_emptied_at is None:
            return 0.0

        delta_minutes = (timezone.now() - self.last_emptied_at).total_seconds() / 60
        return delta_minutes * self.resource_per_minute

    def __str__(self):
        return f"{self.location} ({self.resource_type})"


class EmptyLog(models.Model):
    """A record of when a Skyhook was emptied."""

    skyhook = models.ForeignKey(Skyhook, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), null=True)
    emptied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.skyhook.name} emptied by {self.user} on {self.emptied_at}"
