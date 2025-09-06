# 🛠 register_exception_handlers

`register_exception_handlers(app, ...)` gives your FastAPI app consistent error handling, optional fallback for
unhandled exceptions, structured logging, and an OpenAPI tweak that keeps response shapes stable for clients.

---

## Function signature

```python
def register_exception_handlers(
        app: FastAPI,
        response_format: ResponseFormat = ResponseFormat.RESPONSE_MODEL,
        use_fallback_middleware: bool = True,
        log: bool = True,
        log_traceback: bool = True,
        log_traceback_unhandled_exception: bool = True,
        include_null_data_field_in_openapi: bool = True,
        *,
        log_level: Optional[Literal[10, 20, 30, 40, 50]] = None,
        log_request_context: bool = True,
        log_header_keys: Tuple[str, ...] = (...),
        extra_log_fields: Optional[Callable] = None,
        response_headers: Union[bool, Tuple[str, ...], None] = True,
) -> None:
    ...
```

## Parameters

| Parameter                            | Type                                   | Required | Default                                                                                          | Effect                                                                                                                                                                                  |
|--------------------------------------|----------------------------------------|----------|--------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `app`                                | `FastAPI`                              | Yes      | —                                                                                                | The FastAPI instance to patch with handlers and middleware.                                                                                                                             |
| `response_format`                    | `ResponseFormat`                       | No       | `ResponseFormat.RESPONSE_MODEL`                                                                  | Chooses how errors are serialized. Can be `RESPONSE_MODEL`, `RFC7807`, or `RESPONSE_DICTIONARY`.                                                                                        |
| `use_fallback_middleware`            | `bool`                                 | No       | `True`                                                                                           | Adds a middleware that catches any unhandled exception and returns a safe 500 JSON response.                                                                                            |
| `log`                                | `bool`                                 | No       | `True`                                                                                           | **Global toggle** for all logging (handled + unhandled). If `False`, no logs are written at all.                                                                                        |
| `log_traceback`                      | `bool`                                 | No       | `True`                                                                                           | If `True`, logs traceback for handled `APIException` errors. Useful in development, but can be noisy in prod.                                                                           |
| `log_traceback_unhandled_exception`  | `bool`                                 | No       | `True`                                                                                           | If `True`, logs traceback for unhandled runtime errors caught by the middleware.                                                                                                        |
| `include_null_data_field_in_openapi` | `bool`                                 | No       | `True`                                                                                           | Ensures non-200 OpenAPI examples include `"data": null` for stable schemas in SDKs and validators.                                                                                      |
| `log_level`                          | `int` (10–50)                          | No       | `logger.getEffectiveLevel()`                                                                     | Override logging level for exception logging (`DEBUG=10`, `INFO=20`, etc.).                                                                                                             |
| `log_request_context`                | `bool`                                 | No       | `True`                                                                                           | If `True`, adds selected request headers and context to exception logs.                                                                                                                 |
| `log_header_keys`                    | `Tuple[str, ...]`                      | No       | `("x-request-id","x-correlation-id","x-amzn-trace-id","x-forwarded-for","user-agent","referer")` | Which headers to include in logs when `log_request_context=True`.                                                                                                                       |
| `extra_log_fields`                   | `Callable[[Request, Exception], Dict]` | No       | `None`                                                                                           | Hook to inject custom fields into logs. Signature: `(request, exc) -> Dict[str, Any]`.                                                                                                  |
| `response_headers`                   | `bool \| Tuple[str, ...] \| None`      | No       | `True`                                                                                           | Controls which request headers are echoed back in responses:<br>• `True` → default set (`x-request-id`, etc.)<br>• `False/None` → no headers echoed<br>• `("x-user-id",)` → custom list |

### ResponseFormat options

| Enum                  | Description                                                    | Typical use                                              |
|-----------------------|----------------------------------------------------------------|----------------------------------------------------------|
| `RESPONSE_MODEL`      | Uses your internal `ResponseModel` schema.                     | Default for product APIs that want one consistent shape. |
| `RFC7807`             | Returns RFC 7807 Problem Details (`application/problem+json`). | Public APIs and standards-driven clients.                |
| `RESPONSE_DICTIONARY` | Returns plain dictionaries without models.                     | Ultra lightweight responses or quick prototypes.         |

---

## What is registered

1. **APIException handler**  
   Catches `APIException`, logs request metadata and optional traceback, then serializes using `response_format`.

2. **Validation handler** *(only when `use_fallback_middleware=True`)*  
   Catches `RequestValidationError` and returns 422 either as `ResponseModel` or RFC 7807.

3. **Fallback middleware** *(only when `use_fallback_middleware=True`)*  
   Wraps each request to catch unhandled exceptions and return a uniform 500 response with logging.

4. **OpenAPI patch** *(only when `include_null_data_field_in_openapi=True`)*  
   Modifies generated OpenAPI once to ensure non-200 examples include `"data": null` when missing.

5. **Logging context enhancements**

    - `log_level`: override logging verbosity for exceptions (`DEBUG=10`, `INFO=20`, etc.).
    - `log_request_context`: if enabled, includes contextual request headers in logs.
    - `log_header_keys`: choose which headers are logged (default: `x-request-id`, `user-agent`, etc.).
    - `extra_log_fields`: inject custom structured metadata into logs (e.g. user_id, masked API keys).

6. **Response headers echo**
    - `response_headers=True` → echoes a default set of headers (`x-request-id`, `x-correlation-id`, `x-amzn-trace-id`).
    - `response_headers=False` or `None` → no headers echoed back.
    - `response_headers=("x-user-id",)` → custom list of headers echoed back.

---

## Response shapes

### RESPONSE_MODEL

```json
{
  "status": "fail",
  "message": "Permission denied",
  "description": "You cannot access this resource.",
  "error_code": "PER-403",
  "data": null
}
```

### RFC 7807

Header: `Content-Type: application/problem+json`

```json
{
  "title": "Permission denied",
  "description": "You cannot access this resource.",
  "status": 403,
  "type": "https://example.com/errors/forbidden",
  "instance": "/admin/panel"
}
```

### RESPONSE_DICTIONARY

```json
{
  "data": null,
  "status": "FAIL",
  "message": "Permission denied",
  "error_code": "PER-403",
  "description": "You cannot access this resource."
}
```

---

## Quick start

```python
from fastapi import FastAPI
from api_exception import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
```

---

## Usage patterns

### Minimal

```python
register_exception_handlers(app)
```

### Production with file logging and quieter handled errors

```python
from api_exception import register_exception_handlers, add_file_handler, logger

add_file_handler("prod_errors.log")
register_exception_handlers(
    app,
    log_traceback=False,
    log_traceback_unhandled_exception=True
)
logger.setLevel("WARNING")
```


### Extra logging hooks

•    `log_header_keys`: choose which headers are shown in logs.

•    `extra_log_fields`: inject any additional structured metadata into log records.

Example:

```python
def my_extra_fields(request, exc):
    def mask(value: str, visible: int = 4) -> str:
        """Simple masker: keep last `visible` chars, rest → * """
        if not value or not isinstance(value, str):
            return value
        if len(value) <= visible:
            return "*" * len(value)
        return "*" * (len(value) - visible) + value[-visible:]

    return {
        "user_id": request.headers.get("x-user-id", "anonymous"),
        "custom_tag": "billing-service",
        "has_exception": exc is not None,
        # Mask sensitive headers
        "authorization": mask(request.headers.get("authorization", "")),
        "api_key": mask(request.query_params.get("api_key", "")),
        # Example: mask email except domain
        "email": (lambda e: e if "@" not in e else mask(e.split("@")[0]) + "@" + e.split("@")[1])(
            request.query_params.get("email", "")
        )
    }


register_exception_handlers(app, extra_log_fields=my_extra_fields)
```

---

### Response headers echo

You can make the API echo request headers back in responses.

```python
from api_exception import register_exception_handlers

# Default set
register_exception_handlers(app, response_headers=True)

# Disabled
register_exception_handlers(app, response_headers=False)

# Custom
register_exception_handlers(app, response_headers=("x-user-id",))
```



### RFC 7807 outputs

```python
from api_exception import register_exception_handlers, ResponseFormat

register_exception_handlers(
    app,
    response_format=ResponseFormat.RFC7807,
    include_null_data_field_in_openapi=False
)
```

### No fallback middleware

```python
register_exception_handlers(
    app,
    use_fallback_middleware=False
)
```

### Lightweight dict responses

```python
from api_exception import ResponseFormat, register_exception_handlers

register_exception_handlers(
    app,
    response_format=ResponseFormat.RESPONSE_DICTIONARY
)
```

### Disable all logging (global)

```python
register_exception_handlers(
    app,
    log=False
)
```

---

## Endpoint example

```python
from fastapi import FastAPI, Path, Request
from typing import Optional, Dict, Any
from pydantic import BaseModel
from api_exception import (
    APIException,
    register_exception_handlers,
    ResponseModel, ResponseFormat,
    BaseExceptionCode,
    APIResponse
)

app = FastAPI()


def my_extra_fields(request: Request, exc: Optional[BaseException]) -> Dict[str, Any]:
    # Örn. özel header'ı maskeyle logla
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
                            extra_log_fields=my_extra_fields)


class UserResponse(BaseModel):
    id: int
    username: str


class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("USR-404", "User not found.", "The user ID does not exist.")
    PERMISSION_DENIED = ("PER-403", "Permission denied.", "You cannot access this resource.")


@app.get(
    "/user/{user_id}",
    response_model=ResponseModel[UserResponse],
    responses=APIResponse.custom(
        (403, CustomExceptionCode.PERMISSION_DENIED),
        (404, CustomExceptionCode.USER_NOT_FOUND),
    ),
)
async def get_user(user_id: int = Path(...)):
    if user_id == 1:
        raise APIException(error_code=CustomExceptionCode.USER_NOT_FOUND, http_status_code=404)

    return ResponseModel[UserResponse](
        data=UserResponse(id=2, username="Jane Doe"),
        description="User found successfully."
    )
```

---

## Validation errors

`RequestValidationError` is handled automatically and returns 422.

**ResponseModel mode**

```json
{
  "status": "fail",
  "message": "Validation Error",
  "description": "Field required",
  "error_code": "VAL-422",
  "data": null
}
```

**RFC 7807 mode**

```json
{
  "title": "Validation Error",
  "description": "Field required",
  "status": 422
}
```

---

## OpenAPI behavior

When `include_null_data_field_in_openapi=True`, the generator adds `"data": null` to non-200 examples that already
include the standard error keys. This keeps SDKs and validators happy with a single, stable shape. The patched schema is
cached on `app.openapi_schema`.

---

## Logging

- Every handled `APIException` logs path, method, client IP and optional traceback.
- Unhandled exceptions log a clear header block plus args and message.
- Use `add_file_handler(path)` to also write logs to a file.
- Tune verbosity with `logger.setLevel("DEBUG" | "INFO" | "WARNING" | "ERROR")`.

---

## Troubleshooting

| Symptom                               | Likely cause                                             | Fix                                                                       |
|---------------------------------------|----------------------------------------------------------|---------------------------------------------------------------------------|
| Swagger examples show no `data` field | OpenAPI example lacks `data`                             | Set `include_null_data_field_in_openapi=True` and restart the server.     |
| Responses not in expected shape       | Wrong `response_format` or endpoint `responses` override | Verify `response_format` and your `APIResponse.*` helper usage.           |
| Logs are too noisy                    | `log_traceback=True` in prod                             | Set `log_traceback=False`, keep `log_traceback_unhandled_exception=True`. |
| 422 responses not standardized        | Fallback disabled                                        | Set `use_fallback_middleware=True`.                                       |