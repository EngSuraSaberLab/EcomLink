from django.utils import translation


class AdminLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info or ""
        if path.startswith("/admin/") or "/admin/" in path:
            with translation.override("en"):
                request.LANGUAGE_CODE = "en"
                return self.get_response(request)
        return self.get_response(request)
