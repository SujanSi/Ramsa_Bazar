from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def check_blacklisted(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_blacklisted:
            return HttpResponseForbidden("You are blacklisted and cannot perform this action.")
        return view_func(request, *args, **kwargs)
    return wrapper