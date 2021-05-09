import logging

from . import status


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


class DynamicsException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_detail = "Dynamics Web API call failed."

    def __init__(self, message: str = None):
        self.detail = f"[{self.status_code}] {self.error_detail}"
        if message is not None:
            self.detail += f" - {message}"

        logger.error(self.detail)

    def __str__(self):
        return str(self.detail)


class ParseError(DynamicsException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_detail = "Malformed request."


class AuthenticationFailed(DynamicsException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_detail = "Incorrect authentication credentials."


class PermissionDenied(DynamicsException):
    status_code = status.HTTP_403_FORBIDDEN
    error_detail = "You do not have permission to perform this action."


class NotFound(DynamicsException):
    status_code = status.HTTP_404_NOT_FOUND
    error_detail = "Not found."


class MethodNotAllowed(DynamicsException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    error_detail = 'Method "{method}" not allowed.'

    def __init__(self, method: str, message: str = None):
        if message is None:
            self.error_detail = self.error_detail.format(method=method)
        super().__init__(message)


class DuplicateRecordError(DynamicsException):
    # Could also be a concurrency mismatch, but this is much more common
    status_code = status.HTTP_412_PRECONDITION_FAILED
    error_detail = "Trying to save a duplicate record."


class PayloadTooLarge(DynamicsException):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    error_detail = "Request length is too large."


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
    error_detail = "Dynamics Web API limits were exceeded."


class OperationNotImplemented(DynamicsException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    error_detail = "Requested operation isn't implemented."


class WebAPIUnavailable(DynamicsException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_detail = "Web API service isn't available."
