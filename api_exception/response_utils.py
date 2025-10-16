from typing import Dict, Tuple, Union

# --- Backward-compatible TypeGuard import (Python 3.8–3.9 support) ---
try:
    from typing import TypeGuard  # Python 3.10+
except ImportError:
    from typing_extensions import TypeGuard  # For Python <3.10


from api_exception.response_model import ResponseModel
from api_exception.enums import ExceptionStatus, BaseExceptionCode
from api_exception.rfc7807_model import RFC7807ResponseModel

Item2 = Tuple[int, BaseExceptionCode]
Item4 = Tuple[int, BaseExceptionCode, str, str]
Item = Union[Item2, Item4]


def _is_item2(item: Item) -> TypeGuard[Item2]:
    return len(item) == 2


def _is_item4(item: Item) -> TypeGuard[Item4]:
    return len(item) == 4


class APIResponse:
    """
    Utility class to generate standardized Swagger/OpenAPI responses
    using your ResponseModel for both default and custom errors.
    """

    @staticmethod
    def default() -> Dict[int, dict]:
        """
        Generate default standardized error responses for common HTTP status codes.

        Each response uses your ResponseModel with:
            - 'status' set to FAIL
            - 'data' always set to None since we are dealing with the error cases.
            - 'message', 'description' and 'error_code' specific to the status code

        Useful for quickly adding 400, 401, 403, 404, 500 standard error examples
        to your FastAPI route docs.

        Example:
            responses = APIResponse.default()

        Returns:
            Dict[int, dict]: A dictionary mapping each status code to a
            Swagger/OpenAPI response object that FastAPI can use in the 'responses' parameter.
        """
        examples = {
            400: ("BAD-400", "Bad Request", "Your request is invalid or malformed."),
            401: ("AUTH-401", "Unauthorized", "Authentication credentials were missing or invalid."),
            403: ("PERM-403", "Forbidden", "You do not have permission to access this resource."),
            404: ("RES-404", "Not Found", "The requested resource could not be found."),
            422: ("VAL-422", "Validation Error", "Input validation failed."),
            500: ("INT-500", "Internal Server Error", "An unexpected error occurred on the server.")
        }

        responses: Dict[int, dict] = {}
        for code, (err_code, msg, desc) in examples.items():
            responses[code] = {
                "model": ResponseModel,
                "description": msg,
                "content": {
                    "application/json": {
                        "example": {
                            "data": None,
                            "status": "FAIL",
                            "message": msg,
                            "description": desc,
                            "error_code": err_code
                        }
                    }
                }
            }

        return responses

    @staticmethod
    def custom(*items: tuple[int, 'BaseExceptionCode']):
        """
        Generate one or more custom error responses for FastAPI Swagger docs
        using your defined ExceptionCode enums.

        Each custom response will use your standardized ResponseModel
        with FAIL status, the specified error_code, message, and description.
        The 'data' field will always be None for error cases.

        Args:
            *items: One or more tuples of (HTTP status code, ExceptionCode).
                - status_code (int): The HTTP status code to return.
                - exception_code (BaseExceptionCode): Your custom ExceptionCode entry.

        Example:
        ```python
            from custom_enum.enums import CustomExceptionCode
            from api_exception.response_utils import APIResponse
            responses = APIResponse.custom(
                (403, CustomExceptionCode.PERMISSION_DENIED),
                (401, CustomExceptionCode.INVALID_API_KEY)
            )
        ```

        Returns:
            Dict[int, dict]: A dictionary of status code to response spec,
            ready to be used in FastAPI route 'responses' parameter.
        """
        if not items:
            raise ValueError("At least one (status_code, exception_code) pair must be provided.")
        if not all(isinstance(item, tuple) and len(item) == 2 for item in items):
            raise ValueError("Each item must be a tuple of (status_code, exception_code).")
        if not all(isinstance(item[0], int) for item in items):
            raise ValueError("Each status_code must be an integer.")
        if not all(isinstance(item[1], BaseExceptionCode) for item in items):
            raise ValueError("Each exception_code must be an instance of BaseExceptionCode or its subclass.")

        responses: Dict[int, dict] = {}
        for status_code, exception_code in items:
            example = ResponseModel(
                data=None,
                status=ExceptionStatus.FAIL,
                message=exception_code.message,
                description=exception_code.description,
                error_code=exception_code.error_code
            ).model_dump()

            responses[status_code] = {
                "description": f"Status: {status_code} - {exception_code.error_code}",
                "content": {
                    "application/json": {
                        "example": example
                    }
                }
            }
        return responses

    @staticmethod
    def rfc7807(*items: tuple[int, 'BaseExceptionCode']):
        """
        Generate one or more custom error responses for FastAPI Swagger docs
        using your defined ExceptionCode enums.

        Each custom response will use your standardized ResponseModel
        with FAIL status, the specified error_code, message, and description.
        The 'data' field will always be None for error cases.

        Args:
            *items: One or more tuples of (HTTP status code, ExceptionCode).
                - status_code (int): The HTTP status code to return.
                - exception_code (BaseExceptionCode): Your custom ExceptionCode entry.

        Example:
        ```python
            from custom_enum.enums import CustomExceptionCode
            from api_exception.response_utils import APIResponse
            responses = APIResponse.custom(
                    (401, CustomExceptionCode.INVALID_API_KEY, "https://example.com/errors/unauthorized", "/account/info"),
                    (403, CustomExceptionCode.PERMISSION_DENIED, "https://example.com/errors/forbidden", "/admin/panel"),
                    (422, CustomExceptionCode.VALIDATION_ERROR, "https://example.com/errors/unprocessable-entity", "/users/create")
            )
        ```

        Returns:
            Dict[int, dict]: A dictionary of status code to response spec,
            ready to be used in FastAPI route 'responses' parameter.
        """
        if not items:
            raise ValueError("At least one (status_code, exception_code) pair must be provided.")
        if not all(isinstance(item, tuple) and (len(item) == 2 or len(item) == 4) for item in items):
            raise ValueError(
                "Each item must be a tuple of (status_code, exception_code) or "
                "(status_code, exception_code, type, instance)."
            )

        responses: Dict[int, dict] = {}
        for item in items:
            if _is_item2(item):
                status_code, exception_code = item
                error_type = exception_code.rfc7807_type
                error_instance = exception_code.rfc7807_instance
            elif _is_item4(item):
                status_code, exception_code, error_type, error_instance = item
            else:
                raise ValueError("Invalid item arity.")

            if not isinstance(status_code, int):
                raise ValueError("Each status_code must be an integer.")
            if not isinstance(exception_code, BaseExceptionCode):
                raise ValueError("Each exception_code must be an instance of BaseExceptionCode or its subclass.")

            example = RFC7807ResponseModel(
                instance=error_instance,
                type=error_type,
                title=exception_code.message,
                detail=exception_code.description,
                status=status_code
            ).model_dump()

            responses[status_code] = {
                "description": f"Status: {status_code} - {exception_code.error_code}",
                "content": {
                    "application/problem+json": {
                        "example": example
                    }
                }
            }

        return responses
