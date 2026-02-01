# Advanced Validation Handling Example

This example demonstrates how to extend **APIException** to expose richer validation
and error details while still preserving the unified response contract provided by the library.

It is intentionally designed as an **opt-in, advanced use case**.  
The default behavior of APIException remains unchanged and secure.

---

## What this example shows

This example demonstrates how to:

- Extend `ResponseModel` with additional root-level fields (`request_id`, `error`)
- Automatically expose raw Pydantic validation errors via `exc.errors()`
- Preserve the unified response schema for both **422 validation errors** and **500 unhandled exceptions**
- Fully customize validation and fallback behavior by disabling the library fallback middleware

So you can customize your business level logic while still benefiting from the library's
unified response handling.
---