from typing import Optional, Dict, Any

from fastapi import FastAPI, Path, Header, Request
from pydantic import BaseModel, Field
from api_exception import (
    APIException,
    ExceptionStatus,
    BaseExceptionCode,
    ResponseModel,
    register_exception_handlers,
    APIResponse,
    ResponseFormat,
    logger
)

logger.setLevel("DEBUG")
app = FastAPI()


async def my_extra_fields(request: Request, exc: Optional[BaseException]) -> Dict[str, Any]:
    # Ex: Mask extra fields
    user_id = request.headers.get("x-user-id", "anonymous")
    return {
        "masked_user_id": f"user-{user_id[-2:]}",
        "service": "billing-service",
        "has_exc": exc is not None,
        "exc_type": type(exc).__name__ if exc else None,
    }


register_exception_handlers(app,
                            response_format=ResponseFormat.RESPONSE_MODEL,
                            log_traceback=True,
                            log_traceback_unhandled_exception=False,
                            log_level=10,
                            log=True,
                            response_headers=("x-user-id",),
                            log_request_context=True,
                            log_header_keys=("x-user-id",),
                            extra_log_fields=my_extra_fields
                            )

'''
Custom Exception Class that you can define in your code to make backend error responses standardized and predictable.

To use:
- Extend the `BaseExceptionCode` class
- Define constants as tuples with the following structure:

    (
        error_code: str,
        message: str,
        description: Optional[str],
        rfc7807_type: Optional[str],
        rfc7807_instance: Optional[str]
    )
'''


class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("USR-404", "User not found.", "The user ID does not exist.")
    INVALID_API_KEY = ("API-401", "Invalid API key.", "Provide a valid API key.")
    PERMISSION_DENIED = ("PERM-403", "Permission denied.", "Access to this resource is forbidden.")
    VALIDATION_ERROR = ("VAL-422", "Validation Error", "Input validation failed.")
    TYPE_ERROR = ("TYPE-400", "Type error.", "A type mismatch occurred in the request.")


class UserResponse(BaseModel):
    id: int = Field(..., example=1, description="Unique identifier of the user")
    username: str = Field(..., example="Micheal Alice", description="Username or full name of the user")


class ApiKeyModel(BaseModel):
    api_key: str = Field(..., example="b2013852-1798-45fc-9bff-4b6916290f5b", description="Api Key.")


@app.get(
    "/user/{user_id}",
    response_model=ResponseModel[UserResponse],
    responses=APIResponse.default(),
    description='''
Examples:
- Get user with ID 1: `/user/1` - APIException: If the user ID is 1.
- Get user with ID 2: `/user/2` - TypeError: If the user ID 2.
- Get user with ID 3: `/user/3` - KeyError: If the user ID is 3.
- Get user with ID 4: `/user/4` - IndexError: If the user ID is 4.
- Get user with ID 5: `/user/5` - ZeroDivisionError: If the user ID is 5.
- Get user with ID 6: `/user/6` - RuntimeError: If the user ID is 6.
- Get user with ID 7: `/user/7` - Returns a valid user response.
'''
)
async def get_user(x_user_id: str = Header(default=None),
                   user_id: int = Path(..., description="The ID of the user")):
    if user_id == 1:
        raise APIException(
            error_code=CustomExceptionCode.USER_NOT_FOUND,
            http_status_code=404,
        )

    if user_id == 2:
        raise TypeError("Invalid type provided.")
    if user_id == 3:
        raise KeyError("Missing key in dictionary.")
    if user_id == 4:
        raise IndexError("List index out of range.")
    if user_id == 5:
        raise ZeroDivisionError("Cannot divide by zero.")
    if user_id == 6:
        raise RuntimeError("Unexpected runtime issue.")

    data = UserResponse(id=user_id, username="John Doe")
    return ResponseModel(data=data,
                         description="User fetched successfully.")


@app.get(
    "/apikey",
    response_model=ResponseModel[ApiKeyModel],
    responses=APIResponse.custom(
        (401, CustomExceptionCode.INVALID_API_KEY),
        (422, CustomExceptionCode.VALIDATION_ERROR)
    )
)
async def check_api_key(api_key: str):
    if api_key != "valid_key":
        raise APIException(
            error_code=CustomExceptionCode.INVALID_API_KEY,
            http_status_code=401,
        )
    data = ApiKeyModel(api_key="valid_key")
    return ResponseModel(
        data=data,
        status=ExceptionStatus.SUCCESS,
        message="API key is valid",
        description="The provided API key is valid."
    )


@app.get(
    "/user-basic",
    response_model=ResponseModel[UserResponse],
    responses=APIResponse.custom(
        (401, CustomExceptionCode.INVALID_API_KEY),
        (403, CustomExceptionCode.PERMISSION_DENIED),
        (422, CustomExceptionCode.VALIDATION_ERROR)
    ),
)
async def user_basic():
    is_not_allowed = True
    if is_not_allowed:
        raise APIException(
            error_code=CustomExceptionCode.PERMISSION_DENIED,
            http_status_code=403,
        )
    data = UserResponse(id=1, username="Kutay")
    return ResponseModel[UserResponse](
        data=data,
        description="User retrieved successfully."
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
