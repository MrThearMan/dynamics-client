import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException


__all__ = [
    "DynamicsException",
    "DuplicateRecordError",
    "PayloadTooLarge",
    "APILimitsExceeded",
    "OperationNotImplemented",
    "WebAPIUnavailable",
]


logger = logging.getLogger(__name__)


class DynamicsException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _("Dynamics Web API call failed.")
    default_code = "dynamics_link_failed"


class DuplicateRecordError(APIException):
    # Could also be a concurrency mismatch, but this is much more common
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = _("Trying to save a duplicate record.")
    default_code = "dynamics_duplicate_record"


class PayloadTooLarge(APIException):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    default_detail = _("Request length is too large.")
    default_code = "dynamics_request_too_large"


class APILimitsExceeded(APIException):
    """Error when API protection limits are exceeded. Creates a log entry."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = _("Dynamics Web API limits were exceeded.")
    default_code = "dynamics_api_limits_exceeded"

    def __init__(self, error_message: str, detail=None, code=None):
        super().__init__(detail=detail, code=code)
        #
        # Dynamics Web API service protection limits were exceeded.
        # This can be due to any of the following reasons:
        #
        # 1. Over 6000 requests within a 5 minute sliding window.
        # 2. Combined request execution time exceeded 20 minutes within a 5 minute sliding window.
        # 3. Over 52 concurrent request.
        # 4. Maximum number of API requests per 24 hours exceeded (depends on Dynamics licence).
        #
        # You can read more here:
        # https://docs.microsoft.com/en-us/powerapps/developer/data-platform/api-limits
        # https://docs.microsoft.com/en-us/power-platform/admin/api-request-limits-allocations
        #
        logger.error(f"API limits exceeded. Reason given by the server: {error_message}.")


class OperationNotImplemented(APIException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = _("Requested operation isn't implemented.")
    default_code = "dynamics_operation_not_implemented"


class WebAPIUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _("Web API service isn't available.")
    default_code = "dynamics_link_down"
