"""Tasks."""

# Standard Library
import re
from datetime import datetime

# Third Party
from celery import shared_task

# Django
from django.utils import timezone

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

from .models import Skyhook, VulnerableLog

logger = get_extension_logger(__name__)


RESOURCE_KEYWORDS = ["magmatic gas", "superionic ice"]


def parse_resource(resource_col):
    """Extract resource type and rate from e.g. 'Magmatic Gas (12.6/min)'"""
    lower = resource_col.lower()
    for keyword in RESOURCE_KEYWORDS:
        if keyword in lower:
            match = re.search(r"\(([0-9.]+)/min\)", resource_col, re.IGNORECASE)
            rate = float(match.group(1)) if match else 0.0
            return keyword, rate
    return None, None


def parse_vulnerable_date(date_col):
    """Parse '2026.02.19 11:43:08' into an aware datetime."""
    if not date_col or date_col.strip().lower() == "none":
        return None
    try:
        dt = datetime.strptime(date_col.strip(), "%Y.%m.%d %H:%M:%S")
        return timezone.make_aware(dt)
    except ValueError:
        logger.warning(f"Could not parse date: {date_col}")
        return None


def parse_location(name_col):
    """Extract location from e.g. 'Orbital Skyhook - BZ-BCK III' -> 'BZ-BCK III'"""
    if " - " in name_col:
        return name_col.split(" - ", 1)[1].strip()
    return name_col.strip()


@shared_task
def process_skyhook_data(raw_data: str):
    """
    process skyhook copy paste

    :param raw_data: Description
    :type raw_data: str
    """
    lines = [line for line in raw_data.strip().splitlines() if line.strip()]
    created_count = 0
    updated_count = 0

    for line in lines:
        cols = line.split("\t")
        if len(cols) < 8:
            continue

        resource_type, rate = parse_resource(cols[5])
        if not resource_type:
            continue

        location = parse_location(cols[3])
        next_vulnerable_at = parse_vulnerable_date(cols[7])

        skyhook, created = Skyhook.objects.update_or_create(
            location=location,
            defaults={
                "resource_type": resource_type,
                "resource_per_minute": rate,
                "next_vulnerable_at": next_vulnerable_at,
            },
        )

        if next_vulnerable_at and (
            created or skyhook.next_vulnerable_at != next_vulnerable_at
        ):
            VulnerableLog.objects.create(
                skyhook=skyhook,
                next_vulnerable_at=next_vulnerable_at,
            )

        if created:
            created_count += 1
            logger.debug(f"Created: {skyhook}")
        else:
            updated_count += 1
            logger.debug(f"Updated: {skyhook}")

    logger.debug(f"Done — {created_count} created, {updated_count} updated.")
    return created_count, updated_count
