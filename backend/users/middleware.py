from django.utils import timezone
from users.models import User


class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            # Update at most once per 60 seconds to avoid excessive DB writes
            now = timezone.now()
            if not request.user.last_activity or (now - request.user.last_activity).total_seconds() > 60:
                User.objects.filter(pk=request.user.pk).update(last_activity=now)
        return response
