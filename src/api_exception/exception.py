from __future__ import annotations

import traceback
from typing import Optional, Dict, Union, Any

from .rfc7807_model import RFC7807ResponseModel
from .enums import BaseExceptionCode, ExceptionStatus
from .response_model import ResponseModel

# Default HTTP status codes mapped by status
DEFAULT_HTTP_CODES = {
    ExceptionStatus.SUCCESS: 200,
    ExceptionStatus.WARNING: 400,
    ExceptionStatus.FAIL: 400,
}


def set_default_http_codes(new_map: dict):
    """
    Override the default HTTP status mapping per ExceptionStatus.

    Example
    -------
    >>> from api_exception import ExceptionStatus
    >>> from api_exception import set_default_http_codes
    >>> set_default_http_codes({ExceptionStatus.WARNING: 422})
    """
    DEFAULT_HTTP_CODES.update(new_map)


class APIException(Exception):
    """
    Custom Exception Class for handling exceptions in a standardized way.

    Attributes:
    -----------
    - error_code : BaseExceptionCode
        An instance of BaseExceptionCode, representing the error type.
    - http_status_code : int
        HTTP status code for the exception, defaults to 400 if not specified.
    - status : ExceptionStatus
        Status of the exception, defaults to FAIL.
    - message : str
        Message to be displayed for the exception, defaults to the message from error_code.
    - description : str
        Detailed description of the exception, defaults to the description from error_code.
    - log_exception : bool
        Hint for the handler whether to log this exception. Default True.
    - log_message : str | dict | None
        Extra context to appear in logs (structured). Not logged here; the handler will process it.
    - headers : dict[str, str] | None
        Optional HTTP headers to be merged into the response.
    """

    def __init__(self,
                 error_code: BaseExceptionCode,
                 http_status_code: int = 400,
                 status: ExceptionStatus = ExceptionStatus.FAIL,
                 message: Optional[str] = None,
                 description: Optional[str] = None,
                 log_exception: bool = True,
                 log_message: Optional[Union[str, Dict[str, Any]]] = None,
                 headers: Optional[Dict[str, str]] = None,
                 ):
        """
        Initializes an APIException with a specific error code, HTTP status, and optional message and description.
        Standardized exception for API layers.

        Parameters:
        -----------
        - error_code : ExceptionCode
            Concrete enum value that provides .error_code, .message, .description, rfc7807 fields.
        - http_status_code : int, optional
            HTTP status code for the response, defaults to 400 if not specified.
        - status : ExceptionStatus, optional
            Defaults to ExceptionStatus.FAIL. Logical status used by the response model (SUCCESS/WARNING/FAIL).
        - message : str, optional
            Optional custom message for the exception. Defaults to the message from error_code if None.
        - description : str, optional
            Optional custom detailed description. Defaults to description from error_code if None.
        - log_exception : bool, optional
            If True, logs the exception details. Defaults to True.
        - log_message : str, optional
            Optional custom log message. If provided, it will be logged along with the exception details.
            Defaults to None, meaning no additional log message will be added.
        - headers : dict[str, str] | None
        Optional HTTP headers to be merged into the response.

        """
        # Use provided message or default to the message from the error code
        self.message: str = message if message is not None else error_code.message
        self.error_code: str = error_code.error_code
        self.description: str = description if description is not None else error_code.description
        self.status: ExceptionStatus = status
        self.http_status_code: int = http_status_code or DEFAULT_HTTP_CODES.get(status, 400)
        self.log_exception: bool = log_exception
        self.log_message: Optional[Union[str, Dict[str, Any]]] = log_message
        self.rfc7807_type: str = error_code.rfc7807_type
        self.rfc7807_instance: str = error_code.rfc7807_instance
        self.headers: Dict[str, str] = headers or {}


    def to_response(self) -> dict:
        """
        Converts the exception to a response dictionary.
        Useful for returning standardized JSON responses in an API.

        Returns:
        --------
        dict: A dictionary containing the error_code, status, message, and description.
        """
        return {
            "data": None,
            "error_code": self.error_code,
            "status": self.status.value,
            "message": self.message,
            "description": self.description
        }

    def to_rfc7807_response(self) -> RFC7807ResponseModel:
        """
        Converts the exception to a response dictionary.
        Useful for returning standardized JSON responses in an API.

        Returns:
        --------
        RFC7807ResponseModel: An instance of RFC7807ResponseModel containing the type, instance, title, status, detail.
        """
        return RFC7807ResponseModel(
            type=self.rfc7807_type,
            instance=self.rfc7807_instance,
            title=self.message,
            status=self.http_status_code,
            detail=self.description
        )

    def to_response_model(self,
                          data=None) -> ResponseModel:
        """
        Converts the exception to a ResponseModel instance.
        Useful for returning standardized API responses.

        Returns:
        --------
        ResponseModel: An instance of ResponseModel containing the error details.
        """
        return ResponseModel(
            data=data,
            status=self.status,
            message=self.message,
            error_code=self.error_code,
            description=self.description
        )

    def __str__(self) -> str:  # pragma: no cover - representation
        return f"[{self.error_code}] {self.message} (Status: {self.status}, Description: {self.description})"
