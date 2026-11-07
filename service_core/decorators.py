from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_admin_role:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Administrator privileges required.")
        return redirect('dashboard_redirect')
    return _wrapped_view

def mechanic_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_mechanic_role or request.user.is_admin_role:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Service Mechanic privileges required.")
        return redirect('dashboard_redirect')
    return _wrapped_view

def customer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_customer_role or request.user.is_admin_role:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Customer access required.")
        return redirect('dashboard_redirect')
    return _wrapped_view
