"""Views."""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import EmptyLog, Skyhook


@login_required
@permission_required("lawn_skyhooks.basic_access")
def index(request):
    """Render index view."""
    skyhooks = Skyhook.objects.all()

    # Annotate estimated amounts
    for sh in skyhooks:
        sh.estimated_amount = sh.estimate_current_quantity()

    return render(
        request,
        "lawn_skyhooks/index.html",
        {
            "skyhooks": skyhooks,
        },
    )


@login_required
@permission_required("lawn_skyhooks.basic_access")
def empty_skyhook(request, pk):
    """
    Handles clicking the 'empty' button for a skyhook.
    """
    skyhook = get_object_or_404(Skyhook, pk=pk)

    # Create a log entry for who emptied it
    EmptyLog.objects.create(
        skyhook=skyhook,
        user=request.user,
        emptied_at=timezone.now(),
    )

    # Update the last emptied timestamp
    skyhook.last_emptied_at = timezone.now()
    skyhook.save()

    return redirect("lawn_skyhooks:index")  # Change to your table view name
