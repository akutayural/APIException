from fastapi import FastAPI
from api_exception import (
    APIException,
    BaseExceptionCode,
    register_exception_handlers, APIResponse,
)
from pydantic import BaseModel, Field

from api_exception import ResponseFormat
from api_exception import ResponseModel

app = FastAPI()
register_exception_handlers(app, response_format=ResponseFormat.RFC7807)

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
    INVALID_API_KEY = ("API-401", "Invalid API key.", "Provide a valid API key.", "https://example.com/errors/unauthorized", "/account/info")
    PERMISSION_DENIED = ("PERM-403", "Permission denied.", "Access to this resource is forbidden.", "https://example.com/errors/forbidden", "/admin/panel")
    VALIDATION_ERROR = ("VAL-422", "Validation Error", "Input validation failed.", "https://example.com/errors/unprocessable-entity", "/users/create")


class UserResponse(BaseModel):
    id: int = Field(..., example=1, description="Unique identifier of the user")
    username: str = Field(..., example="Micheal Alice", description="Username or full name of the user")


@app.get(
    "/rfc7807",
    response_model=ResponseModel[UserResponse],
    responses=APIResponse.rfc7807(
        (401, CustomExceptionCode.INVALID_API_KEY, "https://example.com/errors/unauthorized", "/account/info"),
        (403, CustomExceptionCode.PERMISSION_DENIED, "https://example.com/errors/forbidden", "/admin/panel"),
        (422, CustomExceptionCode.VALIDATION_ERROR, "https://example.com/errors/unprocessable-entity", "/users/create")
    ),
)
async def rfc7807_example():
    raise APIException(
        error_code=CustomExceptionCode.PERMISSION_DENIED,
        http_status_code=403,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
