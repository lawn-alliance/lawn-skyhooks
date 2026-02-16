"""
template tags
"""

# templatetags/lawn_skyhooks_tags.py
# Django
from django.template.defaulttags import register


@register.filter
def format_timedelta(td):
    """
    Docstring for format_timedelta

    :param td: Description
    """
    if td is None:
        return "N/A"

    total_seconds = int(td.total_seconds())
    negative = total_seconds < 0
    total_seconds = abs(total_seconds)

    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    formatted = f"{days}d {hours:02d}h {minutes:02d}m {seconds:02d}s"
    return f"-{formatted}" if negative else formatted
