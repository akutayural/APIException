from enum import Enum


class ExceptionStatus(str, Enum):
    """
    Enum for different exception statuses used in APIException.
    Provides a standardized way to indicate the outcome of operations.
    """
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class BaseExceptionCode(Enum):
    """
    Base class for defining standardized exception codes and messages.

    Each exception code should include:
    - error_code: Unique identifier for the error.
    - message: User-friendly description of the error.
    - description: Optional detailed description for additional context.
    - rfc7807_type: Optional A URI reference for the error type, a human-readable document or spec for RFC 7807 format
    - rfc7807_instance: Optional A URI that identifies the specific occurrence of the error for RFC 7807 format
    """

    @property
    def error_code(self):
        return self.value[0]

    @property
    def message(self):
        return self.value[1]

    @property
    def description(self):
        return self.value[2] if len(self.value) > 2 else ""

    @property
    def rfc7807_type(self):
        return self.value[3] if len(self.value) > 3 else ""

    @property
    def rfc7807_instance(self):
        return self.value[4] if len(self.value) > 4 else ""

class ExceptionCode(BaseExceptionCode):
    """
    Standardized exception codes for common errors.

    Each exception code entry should provide:
    - A unique error identifier.
    - A user-friendly message.
    - An optional description for more context.
    """
    AUTH_LOGIN_FAILED = ("AUTH-1000", "Incorrect username and password.",
                         "Failed authentication attempt.",
                         "https://example.com/problems/authentication-error",
                         "/login")
    EMAIL_ALREADY_TAKEN = (
        "RGST-1000",
        "An account with this email already exists.",
        "Duplicate email during registration.",
        "https://example.com/problems/duplicate-registration",
        "/register")
    INTERNAL_SERVER_ERROR = (
        "ISE-500",
        "Internal Server Error",
        "An unexpected error occurred. Please try again later.",
        "https://example.com/problems/internal-server-error",
        "/"
    )
    VALIDATION_ERROR = (
        "VAL-422",
        "Validation Error",
        "Request validation failed. Please check the submitted fields.",
        "https://example.com/problems/validation-error",
        "/"
    )
    # Add other exceptions with descriptions as needed


class ResponseFormat(str, Enum):
    RESPONSE_MODEL = "response_model"
    RESPONSE_DICTIONARY = "response_dict"
    RFC7807 = "rfc7807"
