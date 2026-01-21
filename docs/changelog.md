# 📝 Changelog

All notable changes to APIException will be documented here.
This project uses *Semantic Versioning*.


## [0.2.3] - 2026-01-21
### Improved
- Internal exception handling flow reviewed and stabilised for long-term maintenance.
- Logging paths and async handling verified across all supported Python versions.
- Minor internal refactors to improve readability and future extensibility without changing public APIs.
- Confirmed backward compatibility with all existing `register_exception_handlers` usage patterns.

### Documentation
- README refined with clearer onboarding examples and improved Quickstart section.
- Community & recognition section expanded with external mentions and ecosystem visibility.
- Changelog and docs aligned to reflect current stable usage patterns and production readiness.

### Maintenance
- This release intentionally introduces **no breaking changes**.
- Focused on stability, clarity, and long-term maintainability.
- Actively used in production environments; no migration required for existing users.

---

## [0.2.2] - 2026-01-11
### Fixed
- Replaced deprecated `HTTP_422_UNPROCESSABLE_ENTITY` import with
  `HTTP_422_UNPROCESSABLE_CONTENT` to ensure compatibility with newer
  Starlette versions.
- Added backward-compatible fallback for older Starlette releases to avoid
  breaking existing projects.
- Eliminated deprecation warnings related to HTTP 422 status handling.

### Improved
- Verified full compatibility with **pip**, **uv**, and **Poetry** package managers.
- Confirmed successful installation via:
  - PyPI (`uv add apiexception`)
  - GitHub repository (`uv add git+https://github.com/akutayural/APIException.git`)

---

## [0.2.1] - 2025-10-16
### Added
- **Async support** for `extra_log_fields`:  
  You can now define your callback as an `async def` function and directly use  
  `await request.body()` or other asynchronous operations inside it.  
  Backward compatibility for sync functions is fully preserved.
- **Python 3.9 compatibility restored**:  
  Introduced conditional import of `TypeGuard` via `typing_extensions`  
  to ensure full support for Python 3.9 environments.
- **typing-extensions** added as a dependency for backward-compatible typing features.

### Changed
- `response_utils.py` refactored for cleaner type-safety and full cross-version support.  
- Updated `pyproject.toml`:
  - Python version lowered to `>=3.9,<4.0`
  - Added `typing-extensions>=4.0.0`
- Internal handlers now safely await async results from `extra_log_fields`,  
  ensuring consistent behavior across all exception types.

### Fixed
- Fixed `ImportError` on Python 3.9 caused by direct import of `TypeGuard` from `typing`.
- Minor logging improvements and better exception trace readability.

---


## [0.2.0] - 2025-08-23
### Added
- **Advanced logging customizations** in `register_exception_handlers`:
  - `log_level`: override verbosity for exception logging.
  - `log_request_context`: toggle to include/exclude request headers in logs.
  - `log_header_keys`: define which headers are logged (default: `x-request-id`, `user-agent`, etc.).
  - `extra_log_fields`: inject custom structured metadata into logs (e.g. `user_id`, masked API keys).
- **Response headers echo** in `register_exception_handlers`:
  - `response_headers=True` → default headers echoed back.
  - `response_headers=False` → no headers echoed.
  - `response_headers=("x-user-id",)` → custom headers echoed.
- `APIException` now accepts header parameters (headers can carry custom values into responses).
- **Mypy** support added for static type checking.
- Improved documentation for `register_exception_handlers` with usage patterns, logging, and examples.


### Changed
- Logging format has been revamped → now more structured, readable, and consistent.
- Error logging now includes richer metadata: request path, method, client IP, HTTP version, etc.

### Fixed
- Swagger/OpenAPI sometimes showed inconsistent error schemas when `data` was missing.
- **File structure cleanup**: imports in `__init__.py` were fixed and simplified.  
  The package is now easier to import and fully modular.
- Fixed a type issue where `error_code` was not properly annotated as `BaseExceptionCode`.

---

## [0.1.21] - 2025-08-18
✅ Stable release!
✅ **Initial stable and suggested version**

### Fixed
- Added missing `import traceback` in `__init__.py`.  
  This resolves a `NameError` when using `register_exception_handlers` with traceback logging enabled.

---

## [0.1.20] - 2025-08-18

#### Changed
- Refactored `__init__.py` to use relative imports (`from .module import ...`) for cleaner packaging and better IDE compatibility.
- Unified and simplified `__all__` so developers can import everything directly from `api_exception` (e.g. `from api_exception import ResponseModel, APIException`).

#### Fixed
- Resolved IDE red import warnings when using the library in external projects.
- Improved top-level import resolution and consistency across modules.

---

## [0.1.19] - 2025-08-18

#### Added
- Unified import interface: all core classes and functions can now be imported directly from `api_exception` (e.g. `from api_exception import ResponseModel, APIException`).
- Cleaner `__init__.py` exports with `__all__`.

#### Changed
- Internal imports refactored, simplified folder structure for `enums.py`, `response_model.py`, `rfc7807_model.py`.

#### Fixed
- Example and README imports updated to use new unified style.

---

## [0.1.18] - 2025-08-17

### Added
- Global logging control (`set_global_log`) with `log` param in `register_exception_handlers`.
- RFC7807 full support with `application/problem+json` responses.
- Automatic injection of `data: null` in OpenAPI error examples.

### Changed
- Dependency pins relaxed (`>=` instead of strict `==`).
- Docstrings and examples updated (`use_response_model` → `response_format`).
- Unified error logging (no logs when `log=False`).

### Fixed
- Fallback middleware now returns HTTP 500 instead of 422 for unexpected errors.
- Traceback scope bug fixed in handlers.

---

## [v0.1.17] - 2025-08-11

- `RFC 7807` standard support for consistent error responses (`application/problem+json`)

- OpenAPI (Swagger) schema consistency: nullable fields are now explicitly shown for better compatibility

- `Poetry` support has been added for dependency management

- `uv` support has been added.

- extra logger message param has been added to `APIException` for more detailed logging

- `log_traceback` and `log_traceback_unhandled_exception` parameters have been added to `register_exception_handlers()` for more control over logging behavior

- `log_exception` parameter has been added to `APIException` for more control over logging behavior

- `log_message` parameter has been added to `APIException` for more control over logging behavior

- Logging now uses `add_file_handler()` to write logs to a file

- Logging improvements: now includes exception arguments in logs for better debugging

- Documentation has been updated.    

- Readme.md has been updated. 

---

## [v0.1.16] - 2025-07-22

- setup.py has been updated.

- Documentation has been updated. 

- Readme.md has been updated. 

---

## [v0.1.15] - 2025-07-22

- setup.py has been updated.

- Project name has been updated. Instead of `APIException` we will use `apiexception` to comply with `PEP 625`.

- Documentation has been updated. 

- Readme.md has been updated. 

---

## [v0.1.14] - 2025-07-22

- setup.py has been updated.

- Project name has been updated. Instead of `APIException` we will use `apiexception` to comply with `PEP 625`.

---

## [v0.1.13] - 2025-07-21

- /examples/fastapi_usage.py has been updated.

- 422 Pydantic error has been fixed in APIResponse.default()

- Documentation has been updated.

- Exception Args has been added to the logs.

- Readme has been updated. New gifs have been added.

---

## [0.1.12] - 2025-07-14

- Documentation has been added to the project.

- More examples has been added.

- `__all__` includes more methods.

---

## [0.1.11] - 2025-07-13

- Global exception handlers with fallback middleware

- APIResponse for clean Swagger documentation

- Production-ready logging for all exceptions

---

## [0.1.0] - 2025-06-25

🚀 Prototype started!

- Project scaffolding

- `ResponseModel` has been added

- `APIException` has been added

- Defined base ideas for standardizing error handling
