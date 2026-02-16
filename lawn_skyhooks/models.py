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
        permissions = (
            ("basic_access", "Can access this app"),
            ("view_skyhook_logs", "Can view skyhook logs"),
            ("import_skyhooks", "Can import skyhook data"),
        )


class Skyhook(models.Model):
    """
    Skyhook model
    """

    RESOURCE_TYPE_CHOICES = [
        ("magmatic gas", "Magmatic Gas"),
        ("superionic ice", "Superionic Ice"),
    ]

    location = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the Skyhook location e.g. 'BZ-BCK III'.",
    )
    resource_type = models.CharField(
        max_length=50,
        choices=RESOURCE_TYPE_CHOICES,
    )
    resource_per_minute = models.FloatField(default=0.0)
    last_emptied_at = models.DateTimeField(null=True, blank=True)
    next_vulnerable_at = models.DateTimeField(null=True, blank=True)
    claimed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="claimed_skyhooks",
        help_text="User currently working on emptying this skyhook.",
    )

    claimed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the skyhook was claimed.",
    )

    def estimate_current_quantity(self):
        """
        returns estimate of items in skyhook

        :param self:
        """
        if self.last_emptied_at is None:
            return 0.0
        delta_minutes = (timezone.now() - self.last_emptied_at).total_seconds() / 60
        return delta_minutes * self.resource_per_minute

    def time_until_vulnerable(self):
        """
        time until skyhook is vulnerable

        :param self: Description
        """
        if self.next_vulnerable_at is None:
            return None
        delta = self.next_vulnerable_at - timezone.now()
        return delta if delta.total_seconds() > 0 else None

    def claim(self, user):
        """
        claim skyhook

        :param self: Description
        :param user: Description
        """
        self.claimed_by = user
        self.claimed_at = timezone.now()
        self.save()

    def empty(self, user, amount_taken=0.0):
        """
        empty skyhook

        :param self: Description
        :param user: Description
        :param amount_taken: Description
        """
        self.last_emptied_at = timezone.now()
        self.claimed_by = None
        self.claimed_at = None
        self.save()
        EmptyLog.objects.create(
            skyhook=self,
            user=user,
            amount_taken=amount_taken,
        )

    def is_claimed(self):
        """
        is skyhook claimed

        :param self: Description
        """
        return self.claimed_by is not None

    def __str__(self):
        return f"{self.location} ({self.resource_type})"


class EmptyLog(models.Model):
    """A record of when a Skyhook was emptied."""

    skyhook = models.ForeignKey(Skyhook, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), null=True)
    emptied_at = models.DateTimeField(auto_now_add=True)
    amount_taken = models.FloatField(
        default=0.0, help_text="Amount removed from the Skyhook"
    )

    def __str__(self):
        return f"{self.skyhook.location} emptied by {self.user} on {self.emptied_at} ({self.amount_taken})"


class VulnerableLog(models.Model):
    """
    Vulnerable time log
    """

    skyhook = models.ForeignKey(
        Skyhook, on_delete=models.CASCADE, related_name="vulnerable_logs"
    )
    next_vulnerable_at = models.DateTimeField()
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.skyhook.location} - {self.next_vulnerable_at}"
