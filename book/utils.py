from django.http import HttpResponseForbidden


def admin_or_liberarian_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.groups.filter(name__in=["admin", "liberarian"]).exists():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Admins or Librarians only")
    return wrapper


def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.groups.filter(name="student").exists():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Students only")
    return wrapper