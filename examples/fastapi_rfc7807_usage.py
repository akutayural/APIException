from fastapi import FastAPI, Path
from pydantic import BaseModel, Field
from api_exception import (
    APIException,
    BaseExceptionCode,
    register_exception_handlers,
    APIResponse,
)
from enums.response_scheme import ResponseFormat

app = FastAPI()
register_exception_handlers(app,response_format=ResponseFormat.RFC7807)


'''
Custom Exception Class that you can define in your code to make the backend responses look more standardized.
Just extend the `BaseExceptionCode` and use it. 
'''
class CustomExceptionCode(BaseExceptionCode):
    INVALID_API_KEY = ("API-401", "Invalid API key.", "Provide a valid API key.","https://example.com/errors/unauthorized","/account/info")
    PERMISSION_DENIED = ("PERM-403", "Permission denied.", "Access to this resource is forbidden.", "https://example.com/errors/forbidden", "/admin/panel")
    VALIDATION_ERROR = ("VAL-422", "Validation Error", "Input validation failed.", "https://example.com/errors/unprocessable-entity", "/users/create")


@app.get(
    "/rfc7807",
    responses=APIResponse.rfc7807(
        (401, CustomExceptionCode.INVALID_API_KEY, "https://example.com/errors/unauthorized", "/account/info"),
        (403, CustomExceptionCode.PERMISSION_DENIED, "https://example.com/errors/forbidden", "/admin/panel"),
        (422, CustomExceptionCode.VALIDATION_ERROR, "https://example.com/errors/unprocessable-entity", "/users/create")
    ),
)
async def rfc7807_example():
    raise APIException(
        error_code=CustomExceptionCode.PERMISSION_DENIED,
        http_status_code=403
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)