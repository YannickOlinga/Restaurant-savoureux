from django.shortcuts import redirect
from functools import wraps
from django.urls import reverse

def public_only(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('menu')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def anonymous_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('menu')
        return view_func(request, *args, **kwargs)
    return _wrapped_view 