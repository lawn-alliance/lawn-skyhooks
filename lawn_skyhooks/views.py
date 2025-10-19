"""Views."""

# Django
from django.contrib import messages
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
    """Empty a Skyhook, recording the amount and user."""
    skyhook = get_object_or_404(Skyhook, id=pk)

    if request.method == "POST":
        try:
            amount_taken = float(request.POST.get("amount_taken", 0))
        except ValueError:
            messages.error(request, "Invalid amount entered.")
            return redirect("lawn_skyhooks:index")

        # Update last_emptied_at
        skyhook.last_emptied_at = timezone.now()
        skyhook.save()

        # Record in log
        EmptyLog.objects.create(
            skyhook=skyhook, user=request.user, amount_taken=amount_taken
        )

        messages.success(request, f"{skyhook.location} emptied successfully!")
        return redirect("lawn_skyhooks:index")

    return redirect("lawn_skyhooks:index")
