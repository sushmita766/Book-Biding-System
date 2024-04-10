from functools import wraps
from django.http import HttpResponseForbidden

def seller_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role != 'Seller':
            return HttpResponseForbidden("You are not authorized to perform this action.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
