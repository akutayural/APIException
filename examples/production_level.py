import os
from typing import Literal

import uvicorn
from fastapi import FastAPI, Path, APIRouter
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from api_exception import (
    APIException,
    ExceptionStatus,
    BaseExceptionCode,
    ResponseModel,
    register_exception_handlers,
    APIResponse,
    logger,
    add_file_handler,
    ResponseFormat,
)


# -------------------------# FastAPI Production-Level Application
# This is a production-level FastAPI application that demonstrates how to handle exceptions,
# manage settings, and structure your application for scalability and maintainability.
# It includes multiple services (admin, mobile, public API) with standardized error handling and logging.
# I tried to show how to use the api_exception package in a production-level application.
# -------------------------


# The below Settings class is used to manage application settings.
# It reads environment variables and provides default values.
# Normally, you would have a config.py file for this purpose, but for simplicity, we define it here.
class Settings(BaseSettings):
    IS_PRODUCTION: bool = os.getenv("IS_PRODUCTION", "false").lower() in ("true", "1")
    LOG_FILE_PATH: str = "service.log"


"""
# If you want to set default HTTP codes for different ExceptionStatus,
# you can define them here. This is useful for standardizing responses across your application.
DEFAULT_HTTP_CODES["ERROR"] = 500  # Default HTTP code for ERROR status

# or you can set it directly by uncommenting the below lines.
set_default_http_codes({
    ExceptionStatus.SUCCESS: 200,
    ExceptionStatus.FAIL: 400,
    "UNAUTHORIZED": 401,
})
"""

settings = Settings()

# -------------------------
# Logger level setting based on environment
# -------------------------
# Logs to console by default
# logger.setLevel("WARNING")  # Default to WARNING level
# Set logger level can be based on the environment
if settings.IS_PRODUCTION:
    logger.setLevel("ERROR")
else:
    logger.setLevel("INFO")

# You can also add a file handler to log to a file.
add_file_handler(settings.LOG_FILE_PATH, level=logger.level)


# -------------------------
# Custom Exception Class that you can define in your code to make backend error responses standardized and predictable.
# To use:
# - Extend the `BaseExceptionCode` class
# - Define constants as tuples with the following structure:
#     (
#         error_code: str,
#         message: str,
#         description: Optional[str],
#         rfc7807_type: Optional[str],
#         rfc7807_instance: Optional[str]
#     )
class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("USR-404", "User not found.")
    INVALID_API_KEY = ("API-401", "Invalid API key.", "Provide a valid API key.")
    PERMISSION_DENIED = ("PERM-403", "Permission denied.", "Access to this resource is forbidden.")
    VALIDATION_ERROR = ("VAL-422", "Validation Error", "Input validation failed.")
    TYPE_ERROR = ("TYPE-400", "Type error.", "A type mismatch occurred in the request.")
    ITEM_NOT_FOUND = (
        "ITEM-404", "Item not found.", "The requested item does not exist.",
        "https://example.com/problems/item-not-found")
    ITEM_MISSING = ("ITEM-400", "Item missing.", "The item data is required but not provided.",
                    "https://example.com/problems/item-missing", "/items")


# -------------------------
# Shared Models
# -------------------------
# Normally, you would have a shared models file under /schemas such as items.py, but for simplicity, we define it here.
class Item(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    price: float = Field(..., gt=0)


class ListOfItems(BaseModel):
    items: list[Item] = Field(..., min_items=1, max_items=100,
                              description="List of items with a minimum of 1 and maximum of 100 items.")


class UserResponse(BaseModel):
    id: int = Field(..., example=1, description="Unique identifier of the user")
    username: str = Field(..., example="Micheal Alice", description="Username or full name of the user")


# -------------------------
# APP Router
# -------------------------
app = FastAPI(title="monga-API", docs_url=None, redoc_url=None)
api_router = APIRouter()
app.include_router(router=api_router)

# -------------------------
# Admin App
# -------------------------
admin_app = FastAPI(
    title="Admin Service",
    version="1.0.0",
    description="Admin service for managing items and users. Demonstrates exception handling scenarios.",
    docs_url="/docs"
)

admin_api_router = APIRouter(
    responses={
        400: {"model": ResponseModel[Literal[None]]},
        422: {"description": "Validation Error"},
    }
)
admin_app.include_router(router=admin_api_router)
app.mount("/admin/v1", admin_app)

register_exception_handlers(
    admin_app,
    response_format=ResponseFormat.RESPONSE_MODEL,
    use_fallback_middleware=True,
    # This will use the fallback middleware to handle unhandled exceptions. Highly recommended.
    log_traceback=not settings.IS_PRODUCTION,
    include_null_data_field_in_openapi=True
)

# -------------------------
# Mobile App
# -------------------------
mobile_app = FastAPI(title="Mobile Service", version="1.0.0")
api_router = APIRouter(
    prefix="/mobile/v1",
    tags=["mobile"],
)
mobile_api_router = APIRouter(
    responses={
        400: {"model": ResponseModel[Literal[None]]},
        422: {"description": "Validation Error"},
    }
)
mobile_app.include_router(router=mobile_api_router)
app.mount("/mobile/v1", mobile_app)

register_exception_handlers(
    mobile_app,
    response_format=ResponseFormat.RESPONSE_MODEL,
    use_fallback_middleware=True,
    log_traceback=not settings.IS_PRODUCTION,
    include_null_data_field_in_openapi=False
)

# -------------------------
# Public API App
# -------------------------
api_app = FastAPI(title="Public API Service", version="1.0.0")
api_api_router = APIRouter(
    responses={
        400: {"model": ResponseModel[Literal[None]]},
        422: {"description": "Validation Error"},
    }
)
api_app.include_router(router=api_api_router)
app.mount("/api/v1", api_app)

register_exception_handlers(
    api_app,
    response_format=ResponseFormat.RFC7807,
    use_fallback_middleware=True,
    log_traceback=not settings.IS_PRODUCTION,
    log_traceback_unhandled_exception=not settings.IS_PRODUCTION,
    include_null_data_field_in_openapi=True
)


@admin_app.post("/items",
                response_model=ResponseModel[Item],
                responses=APIResponse.custom(
                    (404, CustomExceptionCode.USER_NOT_FOUND),
                    (400, CustomExceptionCode.TYPE_ERROR),
                    (422, CustomExceptionCode.VALIDATION_ERROR)
                ),
                description="Create a new item. Raises various exceptions based on item name for demonstration purposes."
                            "if the item name is 'book', it raises a default 400 error with ITEM_NOT_FOUND code. "
                            "if the item name is 'shoes', it raises a TypeError. "
                            "if the item name is 'fridge', it raises a KeyError. "
                            "if the item name is 'laptop', it raises an IndexError. "
                            "if the item name is 'phone', it raises a ZeroDivisionError. "
                            "if the item name is 'tablet', it raises a RuntimeError.")
async def create_item(item: Item):
    if item.name == "book":
        raise APIException(
            error_code=CustomExceptionCode.ITEM_NOT_FOUND,
            log_message=f"Item with name '{item.model_dump()}' not found.",
            # This will log extra message in the log file
        )
    if item.name == "shoes":
        raise TypeError("Invalid type provided.")
    if item.name == "fridge":
        raise KeyError("Missing key in dictionary.")
    if item.name == "laptop":
        raise IndexError("List index out of range.")
    if item.name == "phone":
        return 1 / 0  # This will raise ZeroDivisionError
    if item.name == "tablet":
        raise RuntimeError("Unexpected runtime issue.")

    data = Item(name=item.name, price=item.price)
    return ResponseModel[Item](data=data,
                               description="Items fetched successfully.")


@mobile_app.get("/items/{item_id}",
                response_model=ResponseModel[ListOfItems],
                responses=APIResponse.default(),
                description="Retrieve an item by its ID. Raises 404 if the item does not exist.")
async def get_item(item_id: int = Path(..., gt=0)):
    if item_id == 999:
        logger.warning(f"Mobile user requested non-existing item: {item_id}")

        raise APIException(
            error_code=CustomExceptionCode.ITEM_MISSING,
            description="Item not found",
            log_exception=False,  # Disable logging for this specific exception
        )
    data = [Item(name=f"Item {item_id}", price=item_id * 10.0),
            Item(name=f"Item {item_id + 1}", price=(item_id + 1) * 10.0)]
    return ResponseModel[ListOfItems](
        data=ListOfItems(items=data),
        status=ExceptionStatus.SUCCESS,
        message="Items retrieved successfully",
        description="List of items fetched successfully."
    )


@api_app.get("/ping",
             response_model=ResponseModel,
             responses=APIResponse.default(),
             description="Ping endpoint to check if the API is running.")
async def ping():
    logger.info("Ping request received")
    return ResponseModel(data="pong")


@api_app.get("/user/{user_id}",
             response_model=ResponseModel[UserResponse],
             responses=APIResponse.default()
             )
async def get_user(user_id: int = Path(..., description="The ID of the user")):
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
    return ResponseModel(data=data)


if __name__ == "__main__":
    uvicorn.run(
        "examples.production_level:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
