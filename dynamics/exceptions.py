import logging

from . import status

try:
    from rest_framework.exceptions import APIException

except ImportError:
    class APIException(Exception):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        default_detail = "A server error occurred."
        default_code = "error"

        def __init__(self, detail: str = None):
            if detail is None:
                detail = self.default_detail

            self.detail = f"[{self.status_code}] {detail}"
            logger.error(self.detail)

        def __str__(self):
            return str(self.detail)


__all__ = [
    "DynamicsException",
    "ParseError",
    "AuthenticationFailed",
    "PermissionDenied",
    "NotFound",
    "MethodNotAllowed",
    "DuplicateRecordError",
    "PayloadTooLarge",
    "APILimitsExceeded",
    "OperationNotImplemented",
    "WebAPIUnavailable",
]


logger = logging.getLogger(__name__)


class DynamicsException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Dynamics Web API call failed."
    default_code = "dynamics_link_failed"

    def __init__(self, detail=None, code=None, *arg, **kwargs):
        super(DynamicsException, self).__init__(detail, code)


class ParseError(DynamicsException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Malformed request."
    default_code = "dynamics_parse_error"


class AuthenticationFailed(DynamicsException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Incorrect authentication credentials."
    default_code = "dynamics_authentication_failed"


class PermissionDenied(DynamicsException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."
    default_code = "dynamics_permission_denied"


class NotFound(DynamicsException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Not found."
    default_code = "dynamics_not_found"


class MethodNotAllowed(DynamicsException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_detail = 'Method "{method}" not allowed.'
    default_code = "dynamics_method_not_allowed"

    def __init__(self, method: str, detail=None, code=None):
        if detail is None:
            self.default_detail = self.default_detail.format(method=method)
        super().__init__(detail=detail, code=code)


class DuplicateRecordError(DynamicsException):
    # Could also be a concurrency mismatch, but this is much more common
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = "Trying to save a duplicate record."
    default_code = "dynamics_duplicate_record"


class PayloadTooLarge(DynamicsException):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    default_detail = "Request length is too large."
    default_code = "dynamics_request_too_large"


class APILimitsExceeded(DynamicsException):
    """Error when API protection limits are exceeded."""

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

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Dynamics Web API limits were exceeded."
    default_code = "dynamics_api_limits_exceeded"


class OperationNotImplemented(DynamicsException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = "Requested operation isn't implemented."
    default_code = "dynamics_operation_not_implemented"


class WebAPIUnavailable(DynamicsException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Web API service isn't available."
    default_code = "dynamics_link_down"
