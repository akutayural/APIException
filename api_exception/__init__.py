from __future__ import annotations

import logging
import traceback
from typing import Callable, Tuple, Optional, Dict, Any, Iterable, Union, Awaitable
from typing import Literal
import inspect


from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from .rfc7807_model import RFC7807ResponseModel
from .enums import ExceptionCode, ExceptionStatus, BaseExceptionCode, ResponseFormat
from .response_model import ResponseModel
from .logger import logger, add_file_handler, log_with_meta
from .exception import (
    APIException,
    set_default_http_codes,
    DEFAULT_HTTP_CODES,
)
from .response_utils import APIResponse

__all__ = [
    "DEFAULT_HTTP_CODES",
    "APIException",
    "ExceptionCode",
    "BaseExceptionCode",
    "ExceptionStatus",
    "ResponseModel",
    "ResponseFormat",
    "RFC7807ResponseModel",
    "register_exception_handlers",
    "set_default_http_codes",
    "logger",
    "add_file_handler",
    "APIResponse",
]

LogLevelLiteral = Literal[10, 20, 30, 40, 50]
HeaderKeys = Tuple[str, ...]

ExtraLogFields = Callable[
    [Callable[[Request, Optional[BaseException]], Dict[str, Any]]],
    Callable[[Request, Optional[BaseException]], Awaitable[Dict[str, Any]]]
]


def register_exception_handlers(
        app: FastAPI,
        response_format: ResponseFormat = ResponseFormat.RESPONSE_MODEL,
        use_fallback_middleware: bool = True,
        log: bool = True,
        log_traceback: bool = True,
        log_traceback_unhandled_exception: bool = True,
        include_null_data_field_in_openapi: bool = True,
        *,
        # Dev-friendly logging customizations
        log_level: Optional[LogLevelLiteral] = None,  # if None, use current logger level
        log_request_context: bool = True,
        log_header_keys: HeaderKeys = (
                "x-request-id",
                "x-correlation-id",
                "x-amzn-trace-id",
                "x-forwarded-for",
                "user-agent",
                "referer",
        ),
        extra_log_fields: Optional[ExtraLogFields] = None,
        response_headers: Union[bool, HeaderKeys, None] = True,
):
    """
    Attach APIException and fallback handlers to a FastAPI app.

    This ensures that any raised APIException will return a standardized response.
    Optionally, a fallback middleware can catch unhandled exceptions and return
    a consistent error structure.

    Also, it can log the exception details, including the traceback,
    request path, method, and client IP address, exception, exception args and so on.
    This is useful for debugging and monitoring purposes.
    By default, it automatically logs everything related to the exception described above.


    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.
    response_format : ResponseFormat, default=ResponseFormat.RESPONSE_MODEL
        If ResponseFormat.RESPONSE_MODEL, Return error responses using the standard internal response model.
        If ResponseFormat.RFC7807, Return error responses using the RFC 7807 (Problem Details for HTTP APIs) format.
        If ResponseFormat.RESPONSE_DICTIONARY, returns plain dictionaries.
    use_fallback_middleware : bool, default=True
        If True, catches ALL unhandled exceptions (runtime errors, etc.) and logs them.
    log : bool, default=True
        If False, disables **all logging** (including APIException logs and unhandled exceptions).
        Overrides `log_exception` flags inside APIException. Useful for production environments
        where you want standardized responses but no logging output.
    log_traceback : bool, default=True
        If True, logs traceback for APIException errors.
    log_traceback_unhandled_exception : bool, default=True
        If True, logs traceback for unhandled runtime exceptions.
    include_null_data_field_in_openapi : bool, default=True
        If True, this flag ensures that OpenAPI (Swagger) documentation includes `null` as a valid value for nullable fields in response schemas.

    # --- New / Advanced logging controls ---
    log_level : Literal[10, 20, 30, 40, 50] | None, default=None
        Effective logger level used for conditional behaviors inside the handlers.
        If None, uses the current logger level (e.g., set via `logger.setLevel("DEBUG")`).
        Example: `log_level=10` (DEBUG), `log_level=20` (INFO), etc.
    log_request_context : bool, default=True
        If True, selected request headers (see `log_header_keys`) are also added into the `meta` section of logs.
        Set False to avoid logging request headers (for very minimal logs or privacy-sensitive environments).
    log_header_keys : Tuple[str, ...], default=("x-request-id","x-correlation-id","x-amzn-trace-id","x-forwarded-for","user-agent","referer")
        Which request headers to include in log context (`meta`) when `log_request_context=True`.
        Header lookup is case-insensitive; keys are normalized to lower-case.
        Example: `log_header_keys=("x-user-id","x-request-id")`.
    extra_log_fields : Callable[[Request, Optional[BaseException]], Dict[str, Any]] | None, default=None
        A hook to inject **custom** fields into the log `meta`. Receives `(request, exc)` and must return a dict.
        Useful for business context (tenant_id, feature flags, masked user ids, etc.).
        def my_fields(req, exc): ...
        async def my_fields(req, exc): ...
        Example:
            ```python
            def my_extra_fields(req, exc):
                return {"service": "billing", "tenant_id": req.headers.get("x-tenant-id")}
            register_exception_handlers(app, extra_log_fields=my_extra_fields)
            ```
    response_headers : bool | Tuple[str, ...] | None, default=True
        Controls which request headers are **echoed back** on error responses.
        - `True`  → Echo default set: ("x-request-id","x-correlation-id","x-amzn-trace-id")
        - `False`/`None` → Echo nothing
        - `("x-user-id",)` → Echo only the provided headers
            Examples:
            ```python
            register_exception_handlers(app, response_headers=True)              # default set
            register_exception_handlers(app, response_headers=False)             # disable echo
            register_exception_handlers(app, response_headers=("x-user-id",))    # custom echo
            ```

    Examples
    --------
    **1️⃣ Basic usage (default setup):**
    ```python
    from fastapi import FastAPI
    from api_exception import register_exception_handlers

    app = FastAPI()
    register_exception_handlers(app)
    ```

    **2️⃣ Production setup – log to file, disable traceback for handled exceptions (but keep for crashes):**
    ```python
    from fastapi import FastAPI
    from api_exception import register_exception_handlers, add_file_handler, logger

    app = FastAPI()

    # Log to a file for production monitoring
    add_file_handler("prod_errors.log")

    # Only log tracebacks for unhandled runtime errors (not for expected APIExceptions)
    register_exception_handlers(
        app,
        log_traceback=False,
        log_traceback_unhandled_exception=True
    )

    # Increase verbosity for debugging
    logger.setLevel("DEBUG")
    ```

    **3️⃣ Lightweight setup for development – skip fallback middleware and return raw dicts (not ResponseModel):**
    ```python
    from fastapi import FastAPI
    from api_exception import register_exception_handlers

    app = FastAPI()

    register_exception_handlers(
        app,
        use_fallback_middleware=False,   # Let FastAPI's default error pages handle unhandled exceptions
        log=False,
        response_format=ResponseFormat.RESPONSE_DICTIONARY         # Return plain dict responses for speed
    )
    ```

    **4️⃣ Full control setup – log to both console and file, tweak everything:**
    ```python
    from fastapi import FastAPI
    from api_exception import register_exception_handlers, add_file_handler, logger

    app = FastAPI()

    # Log to console (default) and also to file
    add_file_handler("detailed_logs.log")

    # Register with all customizations
    register_exception_handlers(
        app,
        response_format=ResponseFormat.RESPONSE_MODEL,
        use_fallback_middleware=True,
        log=True,
        log_traceback=True,
        log_traceback_unhandled_exception=False,  # Don't log tracebacks for runtime errors and/or
                                                 #  any uncaught errors(db error, 3rd party etc.) (just the message)
        include_null_data_field_in_openapi=False, # Don't show null variables in OpenAPI(Swagger)
    )

    # Set logger level to WARNING for cleaner production logs
    logger.setLevel("WARNING")

    ...

    # Example usage
	@app.get(
    "/example",
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
    ```

    **5️⃣  RFC7807 setup – enable RFC7807-compliant error responses :**
    ```python
    from fastapi import FastAPI
    from api_exception import register_exception_handlers, add_file_handler, logger

    app = FastAPI()

    # Log to console (default) and also to file
    add_file_handler("detailed_logs.log")

    # Register with all customizations
    register_exception_handlers(
        app,
        response_format=ResponseFormat.RFC7807,
        use_fallback_middleware=True,
        log_traceback=True,
        log_traceback_unhandled_exception=False,  # Don't log tracebacks for runtime errors and/or
                                                 #  any uncaught errors(db error, 3rd party etc.) (just the message)
        include_null_data_field_in_openapi=False, # Don't show null variables in OpenAPI(Swagger)
    )

    # Set logger level to WARNING for cleaner production logs
    logger.setLevel("WARNING")

    ...

    # Example usage
    @app.get(
    "/rfc7807",
    response_model=ResponseModel[UserResponse],
    responses=APIResponse.rfc7807(
        (401, CustomExceptionCode.INVALID_API_KEY, "https://example.com/errors/unauthorized", "/account/info"),
        (403, CustomExceptionCode.PERMISSION_DENIED, "https://example.com/errors/forbidden", "/admin/panel"),
        (422, CustomExceptionCode.VALIDATION_ERROR, "https://example.com/errors/unprocessable-entity", "/users/create")
    ))
def rfc7807():
    raise APIException(
        error_code=CustomExceptionCode.PERMISSION_DENIED,
        http_status_code=403,
    )
    ```
    """

    # Validate and freeze header key tuples early
    def _validate_header_keys(keys_iter: Iterable[str]) -> Tuple[str, ...]:
        out = []
        for k in keys_iter:
            if not isinstance(k, str) or not k.strip():
                raise ValueError(f"Invalid header key: {k}")
            out.append(k.strip().lower())  # normalize: lower-case
        return tuple(out)

    log_header_keys = _validate_header_keys(log_header_keys)

    # Determine the effective logging level
    effective_level = log_level if log_level is not None else logger.getEffectiveLevel()

    # ---- helpers -------------------------------------------------------------

    def _collect_headers(req: Request, keys: Iterable[str]) -> Dict[str, str]:
        """
        Return a dict of selected headers present on the request.
        Header name lookup is case-insensitive (Starlette lower-cases header keys).
        """
        out: Dict[str, str] = {}
        for k in keys:
            v = req.headers.get(k)
            if v:
                out[k] = v
        return out

    def _resolve_response_headers_param(value: bool | HeaderKeys | None) -> Tuple[str, ...]:
        default = ("x-request-id", "x-correlation-id", "x-amzn-trace-id")
        if value is True:
            return default
        if not value or value is False:
            return ()
        return _validate_header_keys(value)

    _response_header_keys = _resolve_response_headers_param(response_headers)

    def _response_headers(req: Request) -> Dict[str, str]:
        if not _response_header_keys:
            return {}
        return _collect_headers(req, _response_header_keys)

    # ---- handlers ------------------------------------------------------------

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        # Central place to log raised APIException
        if log and getattr(exc, "log_exception", True) is True:
            meta: Dict[str, Any] = {
                "event": "api_exception",
                "path": request.url.path,
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown",
                "http_version": request.scope.get("http_version", None),
                "error_code": getattr(exc, "error_code", None),
                "status": getattr(exc.status, "value", str(getattr(exc, "status", ""))),
                "http_status": getattr(exc, "http_status_code", None),
            }

            if log_request_context:
                meta.update(_collect_headers(request, log_header_keys))

                # Users can pass any dict/str here; we attach it as structured extra
                frame = traceback.extract_stack()[-3]  # Capture the frame where the exception is raised
                if log_traceback:
                    logger.error(f"Exception Raised in {frame.filename}, line {frame.lineno}")
                    meta.update({
                        "raise_file": frame.filename,
                        "raise_line": frame.lineno
                    })
                logger.error(
                    f"Code: {exc.error_code}, Status: {exc.status}, Description: {exc.description}")
                meta.update({
                    "error_code": exc.error_code,
                    "err_message": exc.message,
                    "status": getattr(exc.status, "value", str(exc.status)),
                    "description": exc.description,
                })

            if getattr(exc, "log_message", None) is not None:
                if isinstance(exc.log_message, dict):
                    meta["extra_log_message"] = jsonable_encoder(exc.log_message)
                elif isinstance(exc.log_message, str):
                    meta["extra_log_message"] = str(exc.log_message)
                else:
                    logger.error(f"`log_message` param type is not correct! It can be [str | dict]")

            if extra_log_fields:
                try:
                    result = extra_log_fields(request, exc)
                    if inspect.isawaitable(result):
                        result = await result
                    if isinstance(result, dict):
                        meta.update(result)
                except Exception:
                    pass

            if log_traceback and effective_level <= logging.DEBUG:
                tb = traceback.format_exc()
                log_with_meta(logging.ERROR, f"APIException: {exc.message}", meta)
                logger.error(f"Traceback:\n{tb}")

            else:
                log_with_meta(logging.ERROR, f"APIException: {exc.message}", meta)

        # Serialize according to selected format
        if response_format == ResponseFormat.RESPONSE_MODEL:
            content = exc.to_response_model().model_dump(exclude_none=False)
            media_type = "application/json"
        elif response_format == ResponseFormat.RFC7807:
            content = exc.to_rfc7807_response().model_dump(exclude_none=False)
            media_type = "application/problem+json"
        else:
            content = exc.to_response()
            media_type = "application/json"

        # Build response headers (echo) and merge user-provided headers (if any)
        base_headers = _response_headers(request)
        # If the exception carries its own headers (e.g., from user-land), merge them
        exc_headers = getattr(exc, "headers", None)
        if isinstance(exc_headers, dict):
            try:
                # ensure str->str mapping
                for k, v in list(exc_headers.items()):
                    if k is None or not str(k).strip() or v is None:
                        exc_headers.pop(k, None)
                base_headers.update({str(k): str(v) for k, v in exc_headers.items()})
            except Exception:
                # don't fail the response for header issues
                pass

        return JSONResponse(
            status_code=exc.http_status_code,
            content=content,
            media_type=media_type,
            headers=base_headers,
        )

    if use_fallback_middleware:

        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            """
            Handles RequestValidationError (422) and returns a standardized response.
            Optional rich logging (path, method, IP, UA, http_version, error count, etc.).
            """
            # First error message cleanup
            try:
                raw = exc.errors()[0].get("msg", "Validation error")
                msg = raw.replace("Value error, ", "") if raw.startswith("Value error, ") else raw
            except Exception:
                msg = "Validation error"

            if log:
                tb = traceback.format_exc()
                meta: Dict[str, Any] = {
                    "event": "validation_error",
                    "path": request.url.path,
                    "method": request.method,
                    "client_ip": request.client.host if request.client else "unknown",
                    "http_version": request.scope.get("http_version", None),
                    "error_count": len(exc.errors()),
                    "first_error": msg,
                }
                if log_request_context:
                    meta.update(_collect_headers(request, log_header_keys))
                if extra_log_fields:
                    try:
                        meta.update(extra_log_fields(request, exc))
                    except Exception:
                        pass

                # Client-side issue -> WARNING; include traceback if level allows
                if log_traceback and effective_level <= logging.DEBUG:
                    log_with_meta(logging.WARNING, f"Validation Error: {msg}\nTraceback:\n{tb}", meta)
                else:
                    log_with_meta(logging.WARNING, f"Validation Error: {msg}", meta)

            # Response body
            err = ExceptionCode.VALIDATION_ERROR
            description = msg or err.description

            if response_format == ResponseFormat.RFC7807:
                content = RFC7807ResponseModel(
                    title=err.message,
                    status=HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=description,
                    type=err.rfc7807_type,
                    instance=err.rfc7807_instance,
                ).model_dump(exclude_none=False)
                media_type = "application/problem+json"
            elif response_format == ResponseFormat.RESPONSE_MODEL:
                content = ResponseModel(
                    data=None,
                    status=ExceptionStatus.FAIL,
                    message=err.message,
                    error_code=err.error_code,
                    description=description,
                ).model_dump(exclude_none=False)
                media_type = "application/json"
            else:
                content = {
                    "data": None,
                    "status": ExceptionStatus.FAIL.value,
                    "message": err.message,
                    "error_code": err.error_code,
                    "description": description,
                }
                media_type = "application/json"

            # Build response headers (echo) and merge user-provided headers (if any)
            base_headers = _response_headers(request)

            # If the exception carries its own headers (unlikely but consistent API)
            exc_headers = getattr(exc, "headers", None)
            if isinstance(exc_headers, dict):
                try:
                    # ensure str->str mapping
                    for k, v in list(exc_headers.items()):
                        if k is None or not str(k).strip() or v is None:
                            exc_headers.pop(k, None)
                    base_headers.update({str(k): str(v) for k, v in exc_headers.items()})
                except Exception:
                    # don't fail the response for header issues
                    pass

            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content=content,
                media_type=media_type,
                headers=base_headers,
            )

        @app.middleware("http")
        async def fallback_exception_middleware(request: Request, call_next: Callable):
            try:
                return await call_next(request)
            except Exception as e:
                tb = traceback.format_exc()

                if log:
                    meta: Dict[str, Any] = {
                        "event": "unhandled_exception",
                        "path": request.url.path,
                        "method": request.method,
                        "client_ip": request.client.host if request.client else "unknown",
                        "http_version": request.scope.get("http_version", None),
                        "exception_type": type(e).__name__,
                        "exception_args": e.args,
                    }
                    if log_request_context:
                        meta.update(_collect_headers(request, log_header_keys))
                    if extra_log_fields:
                        try:
                            meta.update(extra_log_fields(request, e))
                        except Exception:
                            pass

                    if log_traceback_unhandled_exception:
                        log_with_meta(logging.ERROR, f"Unhandled Exception: {e}\nTraceback:\n{tb}", meta)
                    else:
                        log_with_meta(logging.ERROR, f"Unhandled Exception: {e}", meta)

                err = ExceptionCode.INTERNAL_SERVER_ERROR

                if response_format == ResponseFormat.RFC7807:
                    content = RFC7807ResponseModel(
                        title=err.message,
                        status=500,
                        detail=err.description,
                        type=err.rfc7807_type,
                        instance=err.rfc7807_instance,
                    ).model_dump(exclude_none=False)
                    media_type = "application/problem+json"
                elif response_format == ResponseFormat.RESPONSE_MODEL:
                    content = ResponseModel(
                        data=None,
                        status=ExceptionStatus.FAIL,
                        message=err.message,
                        error_code=err.error_code,
                        description=err.description,
                    ).model_dump(exclude_none=False)
                    media_type = "application/json"
                else:
                    content = {
                        "data": None,
                        "status": ExceptionStatus.FAIL.value,
                        "message": err.message,
                        "error_code": err.error_code,
                        "description": err.description,
                    }
                    media_type = "application/json"

                # Build response headers (echo) and merge user-provided headers (if any)
                base_headers = _response_headers(request)

                # If the exception carries its own headers (unlikely but consistent API)
                exc_headers = getattr(e, "headers", None)
                if isinstance(exc_headers, dict):
                    try:
                        # ensure str->str mapping
                        for k, v in list(exc_headers.items()):
                            if k is None or not str(k).strip() or v is None:
                                exc_headers.pop(k, None)
                        base_headers.update({str(k): str(v) for k, v in exc_headers.items()})
                    except Exception:
                        # don't fail the response for header issues
                        pass

                return JSONResponse(
                    status_code=500,
                    content=content,
                    media_type=media_type,
                    headers=base_headers,
                )

    if include_null_data_field_in_openapi:
        """
        Custom OpenAPI schema generator that injects `data: null` into example error responses
        to ensure consistent response shape across all status codes.

        When `openapi_show_null_in_responses` is enabled, this function checks all non-200 
        responses in the OpenAPI schema. If the example response includes the standard 
        error fields (`status`, `message`, `description`, `error_code`) but lacks `data`,
        it injects `"data": null` into the example.

        This helps maintain compatibility with clients that expect a fixed response schema,
        especially when using typed SDKs or schema validators.

        The modified schema is cached in `app.openapi_schema` to prevent regeneration.
        """

        if include_null_data_field_in_openapi:

            from typing import Any, Dict

            original_openapi = app.openapi

            def openapi() -> Dict[str, Any]:
                if not app.openapi_schema:
                    schema = original_openapi()
                    paths = schema.get("paths") or {}
                    for path_k, path_v in paths.items():
                        for method_k, method_v in (path_v or {}).items():
                            if "responses" in method_v:
                                for response_k, response_v in method_v["responses"].items():
                                    if response_k == "200":
                                        continue
                                    content = response_v.get("content") or {}
                                    for _, content_v in content.items():
                                        example = content_v.get("example")
                                        if (
                                                isinstance(example, dict)
                                                and "status" in example
                                                and "message" in example
                                                and "description" in example
                                                and "error_code" in example
                                                and "data" not in example
                                        ):
                                            example["data"] = None
                    app.openapi_schema = schema
                return app.openapi_schema

            app.openapi = openapi  # type: ignore[method-assign]
