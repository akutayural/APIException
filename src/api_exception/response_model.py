from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field
from api_exception.enums import ExceptionStatus

# Generic type for response data
DataT = TypeVar('DataT')


class ResponseModel(BaseModel, Generic[DataT]):
    """
    Pydantic model for standardizing successful and unsuccessful API responses.

    Attributes:
    -----------
    - data : Optional[`DataT`]
        The main content of the response. Can be `any` type (TypeVar('DataT')), defaults to `None`. It will be `None` in error responses.
        In abstract, server response payload.
    - status : `ExceptionStatus`
        The status of the response, defaults to SUCCESS. Will be 'FAIL' in error responses. ['SUCCESS', 'WARNING', 'FAIL']
        In abstract, server response status.
    - message : `str`
        Message providing additional context, defaults to a generic success message.
        In abstract, server response message.
    - error_code : Optional[`str`]
        Optional error code, typically None for successful responses.
        In Abstract, server response error code when there is an error.
    - description : Optional[`str`]
        Optional detailed description of the response. Defaults to `None`, but can provide more context in success/error responses.
        In abstract, server response detail.

    Usage [Skip Reading This Part If You Are Not Developing the Backend]:
    ------
    This model can be used to standardize API responses in FastAPI applications. It allows for a consistent structure across successful and error responses, making it easier for clients to handle responses uniformly.

    Example:
         Create a CustomEnumClass extending the BaseExceptionCode to define specific error codes
         with their messages and descriptions. CustomEnumClass(BaseExceptionCode) can be used to define specific error codes with their messages and descriptions.

    Successful Response Example:
    ```python
    from custom_enum.enums import ExceptionStatus
    from schemas.response_model import ResponseModel
    from typing import Dict, Any
    response = ResponseModel(
        data={"user_id": 1, "name": "John Doe"},
        status=ExceptionStatus.SUCCESS,
        message="User found successfully.",
        error_code=None,
        description="The user has been retrieved from the database."
    )
    response.json()
    ```

    This will produce a JSON response like:
    ```json
    {
        "data": {"user_id": 1, "name": "John Doe"},
        "status": "SUCCESS",
        "message": "User found successfully.",
        "error_code": null,
        "description": "The user has been retrieved from the database."
    }
    ```

    Error Response Example:
    ```python

    # Define a custom ExceptionCode class for specific application errors

    class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("USR-404", "User not found.", "The specified user does not exist in the system.")
    INVALID_API_KEY = ("API-401", "Invalid API key provided.", "Please provide a valid API key.")
    PERMISSION_DENIED = ("PERM-403", "Permission denied.", "You do not have permission to access this resource.")

    @app.get("/user",
         response_model=ResponseModel,
         responses=APIResponses.default()
         )
    async def restricted_access():
        raise APIException(
            error_code=CustomExceptionCode.USER_NOT_FOUND,
            http_status_code=403,
        )
    ```

    This will produce a JSON response like:
    ```json
    {
        "data": null,
        "status": "FAIL",
        "message": "User not found.",
        "error_code": "USR-404",
        "description": "The specified user does not exist in the system."
    }
    ```

    """
    data: Optional[DataT] = Field(
        default=None,
        description="Main content of the response, can be `any` type. Defaults to `None`. "
                    "Error responses may not include data. Useful for successful responses.",
        # examples=[({"user_id": 1, "name": "John Doe"}, {"user_id": 2, "name": "Jane Smith"}), [], {}, None]
    )
    status: ExceptionStatus = Field(
        default=ExceptionStatus.SUCCESS,
        description="Status of the response, defaults to SUCCESS. `str` ['SUCCESS', 'WARNING', 'FAIL']",
        examples=["SUCCESS", "WARNING" , "FAIL"]
    )
    message: str = Field(
        default="Operation completed successfully.",
        description="Message providing context for the response. Type: `str`"
    )
    error_code: Optional[str] = Field(
        default=None,
        description="Optional error code, typically 'None' for successful responses. Error code will be used to cover error cases. It will return `str` in the error cases.",
        examples=[None, "AUTH-1000", "USR-404", "API-401", "PERM-403"]
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional detailed description of the response. Defaults to `None`, but can provide more context in success/error responses. Type `str`",
        examples=["Some more detail about the response or the message.", "User has been found.", "Account details have been provided.", "Permission denied."]
    )

