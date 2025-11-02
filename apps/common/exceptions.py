import json
import logging
import traceback

from rest_framework.views import exception_handler as drf_handler

logger = logging.getLogger("apps.common.exceptions")


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler for consistent structured logging and response shaping.
    """
    response = drf_handler(exc, context)
    request = context.get("request")
    view = context.get("view")

    payload = {
        "path": getattr(request, "path", ""),
        "method": getattr(request, "method", ""),
        "user": getattr(getattr(request, "user", None), "pk", None),
        "status": getattr(response, "status_code", 500),
        "view": getattr(view, "__class__", type("Anonymous", (), {})).__name__,
        "exception": exc.__class__.__name__,
        "details": getattr(getattr(response, "data", None), "copy", lambda: None)(),
    }
    formatted_payload = json.dumps(payload, ensure_ascii=False, default=str)

    if payload["status"] >= 500:
        logger.error(
            f"Internal server error | Payload: {formatted_payload}\nTraceback:"
            f" {traceback.format_exc()}"
        )
    elif payload["status"] >= 400:
        logger.warning(f"Client error | Payload: {formatted_payload}")
    else:
        logger.info(f"Handled exception | Payload: {formatted_payload}")
    return response
