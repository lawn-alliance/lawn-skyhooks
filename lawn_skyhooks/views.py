"""Views."""

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Skyhook
from .tasks import process_skyhook_data


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
    Docstring for empty_skyhook

    :param request: Description
    :param pk: Description
    """
    skyhook = get_object_or_404(Skyhook, id=pk)

    if request.method == "POST":
        try:
            amount_taken = float(request.POST.get("amount_taken", 0))
        except ValueError:
            messages.error(request, "Invalid amount entered.")
            return redirect("lawn_skyhooks:index")

        skyhook.empty(request.user, amount_taken)
        messages.success(request, f"{skyhook.location} emptied successfully!")
        return redirect("lawn_skyhooks:index")

    return redirect("lawn_skyhooks:index")


@login_required
@permission_required("lawn_skyhooks.basic_access")
def claim_skyhook(request, pk):
    """
    Docstring for claim_skyhook

    :param request: Description
    :param pk: Description
    """
    skyhook = get_object_or_404(Skyhook, id=pk)

    if request.method == "POST":
        skyhook.claim(request.user)
        messages.success(request, f"{skyhook.location} claimed!")
        return redirect("lawn_skyhooks:index")

    return redirect("lawn_skyhooks:index")


@login_required
@permission_required("lawn_skyhooks.basic_access")
def import_data(request):
    """Render import view and handle data submission."""
    if request.method == "POST":
        raw_data = request.POST.get("raw_data", "")
        process_skyhook_data.delay(raw_data)
        messages.success(request, "Data sent for processing!")
        return redirect("lawn_skyhooks:index")

    return render(request, "lawn_skyhooks/import.html")
