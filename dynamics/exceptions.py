from inspect import cleandoc

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException

from common.utils import send_threaded_mail


__all__ = [
    "DynamicsException",
    "DuplicateRecordError",
    "PayloadTooLarge",
    "APILimitsExceeded",
    "OperationNotImplemented",
    "WebAPIUnavailable",
]


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
    """Error when API protection limits are exceeded. Sends a service email when it occurs."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = _("Dynamics Web API limits were exceeded.")
    default_code = "dynamics_api_limits_exceeded"

    def __init__(self, error_message: str, detail=None, code=None):
        super().__init__(detail=detail, code=code)
        send_threaded_mail(
            subject="Dynamics Web API limits exceeded",
            message=cleandoc(
                f"""
                    Dynamics Web API service protection limits were exceeded for Joki online booking service. 
                    This can be due to any of the following reasons:
                    
                    1. Over 6000 requests within a 5 minute sliding window.
                    2. Combined request execution time exceeded 20 minutes within a 5 minute sliding window.
                    3. Over 52 concurrent request.
                    4. Maximum number of API requests per 24 hours exceeded (depends on Dynamics licence).
                    
                    Reason given by the server:
                    {error_message}
                    
                    This error should not have occured with the expected traffic on the site taken into account.
                    Therefore, either traffic has grown significantly from what was specified, or
                    there are some malicious users making request with the API.
                    
                    If no malicious users are detected, there are a few ways to increase the the limits.
                    You can either configure new Dynamics API users and balance the requests between them, or
                    increase the amount of webservers Dynamics is using, since the limits are enforced per web server.
                    
                    You can read more here:
                    https://docs.microsoft.com/en-us/powerapps/developer/data-platform/api-limits
                    https://docs.microsoft.com/en-us/power-platform/admin/api-request-limits-allocations
                """
            ),
            from_email=None,
            recipient_list=[email for name, email in settings.ADMINS],
        )


class OperationNotImplemented(APIException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = _("Requested operation isn't implemented.")
    default_code = "dynamics_operation_not_implemented"


class WebAPIUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _("Web API service isn't available.")
    default_code = "dynamics_link_down"
