import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ActivityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the user activity
        user = request.user if request.user.is_authenticated else "Anonymous"
        logger.info(
            f"{datetime.now()} - {user} accessed {request.path} from {request.META.get('REMOTE_ADDR')}"
        )

        response = self.get_response(request)
        return response
