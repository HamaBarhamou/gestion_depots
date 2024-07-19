# comptes/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class CheckActiveStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and request.user.role == "fournisseur"
            and not request.user.active
        ):
            messages.error(
                request,
                "Votre compte est inactif. Veuillez contacter l'administrateur.",
            )
            return redirect(reverse("logout"))
        response = self.get_response(request)
        return response
