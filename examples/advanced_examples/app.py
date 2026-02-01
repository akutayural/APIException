from __future__ import annotations

import uuid
import traceback
from typing import Any, Callable, Generic, Optional, TypeVar, List

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api_exception import (
    register_exception_handlers,
    ResponseModel,
    ExceptionCode,
    ExceptionStatus, APIException,
)

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------

app = FastAPI(title="APIException Advanced Validation Handling Example")

# Disable library fallback middleware/handlers so we can fully customize:
# - validation (422) response body
# - unhandled exceptions (500) response body
register_exception_handlers(app,
                            use_fallback_middleware=False,
                            log=True)

DataT = TypeVar("DataT")


# -----------------------------------------------------------------------------
# Custom response model
# -----------------------------------------------------------------------------

class CustomResponseModel(ResponseModel[DataT], Generic[DataT]):
    """
    Extends the library's ResponseModel without breaking the unified response contract.

    Adds:
    - request_id: infrastructure id
    - error: raw Pydantic validation errors (exc.errors())
    """
    request_id: Optional[str] = Field(default=None, description="Infrastructure request id.")
    error: Optional[List[dict[str, Any]]] = Field(
        default=None,
        description="Raw Pydantic validation errors (exc.errors()).",
    )


# -----------------------------------------------------------------------------
# Middleware: ensure request_id
# -----------------------------------------------------------------------------

@app.middleware("http")
async def ensure_request_id(request: Request, call_next: Callable):
    rid = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = rid

    response = await call_next(request)

    # Echo back for client correlation
    response.headers["x-request-id"] = rid
    return response


# -----------------------------------------------------------------------------
# Validation error handler: 422
# -----------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def custom_validation_handler(request: Request, exc: RequestValidationError):
    err = ExceptionCode.VALIDATION_ERROR

    errors = exc.errors() or []
    first_msg = errors[0].get("msg", err.description) if errors else err.description

    return JSONResponse(
        status_code=422,
        content=CustomResponseModel(
            request_id=getattr(request.state, "request_id", None),
            data=None,
            status=ExceptionStatus.FAIL,
            message=err.message,
            error_code=err.error_code,
            description=first_msg,
            error=errors,  # automatic raw pydantic output
        ).model_dump(exclude_none=False),
    )


# -----------------------------------------------------------------------------
# Fallback middleware: 500
# -----------------------------------------------------------------------------

@app.middleware("http")
async def custom_fallback_middleware(request: Request, call_next: Callable):
    try:
        return await call_next(request)
    except Exception:
        err = ExceptionCode.INTERNAL_SERVER_ERROR

        # Recommended: log traceback server-side, do not expose in production responses.
        tb = traceback.format_exc()

        return JSONResponse(
            status_code=500,
            content=CustomResponseModel(
                request_id=getattr(request.state, "request_id", None),
                data=None,
                status=ExceptionStatus.FAIL,
                message=err.message,
                error_code=err.error_code,
                description=err.description,
                # Keep it minimal for safety. If you want, you can include tb here,
                # but it is not recommended for production.
                error=[{"type": "unhandled_exception"}],
            ).model_dump(exclude_none=False),
        )


# -----------------------------------------------------------------------------
# Demo endpoints
# -----------------------------------------------------------------------------

class DemoQuery(BaseModel):
    limit: int
    itemsPerPage: int


class DemoBody(BaseModel):
    limit: int
    itemsPerPage: int


@app.get("/demo/validation", response_model=CustomResponseModel[DemoQuery])
async def demo_validation(limit: int, itemsPerPage: int, request: Request):
    """
    Example:
      GET /demo/validation?limit=dw&itemsPerPage=pops
    This will trigger RequestValidationError and return 422 with error=exc.errors()
    """
    data = DemoQuery(limit=limit, itemsPerPage=itemsPerPage)
    return CustomResponseModel[DemoQuery](
        request_id=request.state.request_id,
        data=data,
        status=ExceptionStatus.SUCCESS,
        message="Everything's good!",
        description="Validation passed.",
        error=None,
    )


@app.post("/demo/validation-body", response_model=CustomResponseModel[DemoBody])
async def demo_validation_body(payload: DemoBody, request: Request):
    if payload.limit < 0:
        raise APIException(
            error_code=ExceptionCode.VALIDATION_ERROR,
            http_status_code=422,
            message="Limit must be non-negative.",
            description="The 'limit' field cannot be less than zero.",
            log_exception=True
        )

    return CustomResponseModel[DemoBody](
        request_id=request.state.request_id,
        data=payload,
        status=ExceptionStatus.SUCCESS,
        message="Everything's good!",
        description="Validation passed.",
        error=None,
    )


@app.get("/demo/crash", response_model=CustomResponseModel[None])
async def demo_crash(request: Request):
    """
    Example:
      GET /demo/crash
    This will raise an unhandled exception and return 500 with unified response schema.
    """
    _ = 1 / 0
    return CustomResponseModel[None](
        request_id=request.state.request_id,
        data=None,
        status=ExceptionStatus.SUCCESS,
        message="Everything's good!",
    )





if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)