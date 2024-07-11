# comptes/decorators.py
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps


def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            if not hasattr(request.user, "role") or request.user.role != role:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
