<link rel="icon" type="image/x-icon" href="favicon/favicon.ico">

# APIException: Standardised Exception Handling for FastAPI


---

## ⚡ Quick Installation
Download the package from PyPI and install it using pip:
```bash
pip install apiexception
```
![Installing the APIException for FastAPI](assets/apiexception-indexPipInstallApiexception.gif)


If you already have **[Poetry](https://python-poetry.org/docs/)** and
the **[uv](https://docs.astral.sh/uv/)** together, you can install it with:

```bash
uv add apiexception
```

```bash
# You can also use the `uv` command to install it:
uv pip install apiexception

# Or, if you prefer using Poetry:
poetry add apiexception
```

After installation, verify it’s working:
```bash
pip show apiexception
```
---

Now that you have the package installed, let’s get started with setting up your FastAPI app.
Just import the `register_exception_handlers` function from `apiexception` and call it with your FastAPI app instance to set up global exception handling:

```python
from api_exception import register_exception_handlers
from fastapi import FastAPI

app = FastAPI()
register_exception_handlers(app=app)
```
That’s it — copy, paste, and you’re good to go. So easy, isn't it? 


!!! tip "Pro tip"
    👉 For advanced configuration, see [**register_exception_handlers reference**](usage/register_exception_handlers.md)


Now all your endpoints will return consistent `success` and `error` responses, and your Swagger docs will be beautifully documented.
Exception handling will be logged, and unexpected errors will return a clear JSON response instead of FastAPI’s default HTML error page.

---
## 🔍 **See It in Action!**

```python
from typing import List
from fastapi import FastAPI, Path
from pydantic import BaseModel, Field
from api_exception import (
    APIException,
    BaseExceptionCode,
    ResponseModel,
    register_exception_handlers,
    APIResponse
)

app = FastAPI()

# Register exception handlers globally to have the consistent
# error handling and response structure
register_exception_handlers(app=app)


# Define your custom exception codes extending BaseExceptionCode
class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("USR-404", "User not found.", "The user ID does not exist.")
    INVALID_API_KEY = ("API-401", "Invalid API key.", "Provide a valid API key.")
    PERMISSION_DENIED = ("PERM-403", "Permission denied.", "Access to this resource is forbidden.")


# Let's assume you have a UserModel that represents the user data
class UserModel(BaseModel):
    id: int = Field(...)
    username: str = Field(...)


# Create the validation model for your response.
class UserResponse(BaseModel):
    users: List[UserModel] = Field(..., description="List of user objects")


@app.get("/user/{user_id}",
         response_model=ResponseModel[UserResponse],
         responses=APIResponse.default()
         )
async def user(user_id: int = Path()):
    if user_id == 1:
        raise APIException(
            error_code=CustomExceptionCode.USER_NOT_FOUND,
            http_status_code=401,
        )
    if user_id == 3:
        a = 1
        b = 0
        c = a / b  # This will raise ZeroDivisionError and be caught by the global exception handler
        return c

    users = [
        UserModel(id=1, username="John Doe"),
        UserModel(id=2, username="Jane Smith"),
        UserModel(id=3, username="Alice Johnson")
    ]
    data = UserResponse(users=users)
    return ResponseModel[UserResponse](
        data=data,
        description="User found and returned."
    )
```

When you run your FastAPI app and open **Swagger UI** (`/docs`),  
your endpoints will display **clean, predictable response schemas** like this below:

<video autoplay loop muted playsinline width="900">
  <source src="assets/apiexception-indexBasicUsage-1.mp4" type="video/mp4">
</video>



#### - Successful API Response? 
```json
{
  "data": {
    "users": [
      {
        "id": 1,
        "username": "John Doe"
      },
      {
        "id": 2,
        "username": "Jane Smith"
      },
      {
        "id": 3,
        "username": "Alice Johnson"
      }
    ]
  },
  "status": "SUCCESS",
  "message": "Operation completed successfully.",
  "error_code": null,
  "description": "User found."
}
```
#### - Error API Response? 
```json
{
  "data": null,
  "status": "FAIL",
  "message": "User not found.",
  "error_code": "USR-404",
  "description": "The user ID does not exist."
}
```
In both cases, the response structure is **consistent**.

- In the example above, when the `user_id` is `1`, it raises an `APIException` with a custom `error_code`, the response is formatted according to the `ResponseModel` and it's logged **automatically** as shown below:

![apiexception-indexApiExceptionLog.png](advanced/exception_1.png)


#### - Uncaught Exception API Response?

What if you forget to handle an exception such as in the [**example**](#see-it-in-action) above?

- When the `user_id` is `3`, the program automatically catches the `ZeroDivisionError` and returns a standard error response, logging it in a **clean structure** as shown below:

```json
{
  "data": null,
  "status": "FAIL",
  "message": "Something went wrong.",
  "error_code": "ISE-500",
  "description": "An unexpected error occurred. Please try again later."
}
```

![apiexception-indexApiExceptionLog.png](advanced/exception_2.png)

### 💡 Clear & Consistent Responses
- 🟢 **200**: Success responses are always documented with your data model.
- 🔑 **401 / 403**: Custom error codes & messages show exactly what clients should expect.
- 🔍 No guesswork — frontend, testers, and API consumers always know what to expect for both **success** and **error** cases.
- 💪 Even **unexpected server-side issues** (DB errors, unhandled exceptions, third-party failures) return a **consistent JSON** that follows your `ResponseModel`.
- ❌ No more raw HTML `500` pages! Every error is logged automatically for an instant audit trail.

---


### 💡 Frontend Integration Advantages
In most APIs, the frontend must:

  1. Check the HTTP status code  
  2. Parse JSON  
  3. Extract data or error details  

With **APIException**, every response follows the same schema: 

  → Simply parse JSON **once** and check the `status` field (`SUCCESS` or `ERROR`).  
  → If `ERROR`, read `error_code` and `message` (or/and `description`) for full details. Since even the unexpected errors are formatted consistently, the frontend can handle them uniformly.


| Flow                  | Steps                                                                 | What the frontend checks                          |
|-----------------------|-----------------------------------------------------------------------|---------------------------------------------------|
| Typical REST          | 1) Check HTTP status → 2) Parse JSON → 3) Branch for data/error      | Status code, JSON shape, error payload variations |
| **With APIException** | **1) Parse JSON once**                                                | Read `status` → `SUCCESS` or `ERROR`              |

**Client pattern:**

```ts
// Example: fetch wrapper / interceptor
const res = await fetch(url, opts);
const body = await res.json();            // same shape for 2xx/4xx/5xx

if (body.status === "SUCCESS") {
  return body.data;                       // ✅ consume data directly
} else {
  throw { code: body.error_code, message: body.description }; // ❌ unified error
}
```

---

### 💡 Backend Maintainability Advantages
- Define each `CustomExceptionCode` **once** with `error_code`, `message`, and `description`.
- Logs become cleaner and easier to search.  
  → If another team reports an `error_code`, you can instantly locate it in logs.  
- Keeps backend code organized and avoids scattering error definitions everywhere.
- Share the `error_code` list with frontend teams for **zero-guesswork** integrations.

---

### 🔍 Logging & Debugging Flexibility
- Toggle tracebacks on/off depending on the environment.
- Fully controllable logging: import, set log levels, or disable entirely.
- **RFC 7808** support out of the box for teams that require standard-compliant error formats.


!!! tip "Pro Tip: Master Your Logs"
    For advanced logging configuration and real-world examples, check out the  
    [**Logging & Debug Guide**](advanced/logging.md).  
    Learn how to add file handlers, mask sensitive data, and keep production logs clean & actionable.

---
Reduces boilerplate and speeds up integration.
This is how **APIException** helps you build trustable, professional APIs from day one!

## 👥 Who should use this?

✅ FastAPI developers who want consistent success & error responses.  
✅ Teams building multi-client or external APIs.  
✅ Projects where Swagger/OpenAPI docs must be clear and human-friendly.  
✅ Teams that need extensible error code management.

If you’re tired of:

- Inconsistent response structures,

- Confusing Swagger docs,

- Messy exception handling,

- Finding yourself while trying to find the exception that isn't logged

- Backend teams asking *“What does this endpoint return?”*,

- Frontend teams asking *“What does this endpoint return in error?”*,

then this library is **for you**.

## 🎯 **Why did I build this?**

After **4+ years** as a FastAPI backend engineer, I’ve seen how **crucial a clean, predictable response model** is.  
When your API serves multiple frontends or external clients, having different JSON shapes, missing status info, or undocumented error codes turns maintenance into chaos.

So, this library:

✅ Standardizes **all** success & error responses,  
✅ Documents them **beautifully** in Swagger,  
✅ Provides a robust **ExceptionCode** pattern,  
✅ Adds an optional **global fallback** for unexpected crashes — all while keeping FastAPI’s speed.

---

## ✨ Core Principles

| Principle | Description |
|-----------|-------------|
| 🔒 **Consistency** | Success and error responses share the exact same structure, improving reliability and DX. |
| 📊 **Clear Docs** | OpenAPI/Swagger remains clean, accurate, and human-friendly. |
| 🪶 **Zero Boilerplate** | Configure once, then use anywhere with minimal repetitive code. |
| ⚡ **Extensible** | Fully customizable error codes, handlers, and response formats for any project need. |

---

## 📊 Benchmark

We benchmarked **apiexception's** `APIException` against **FastAPI's** built-in `HTTPException` using **Locust** with **200** concurrent users over **2 minutes**.  
Both apps received the same traffic mix (≈75% `/ok`, ≈25% `/error`).

| Metric                    | HTTPException (Control App) | APIException (Test App) |
|---------------------------|-----------------------------|-------------------------|
| Avg Latency               | **2.00 ms**                 | 2.72 ms                 |
| P95 Latency               | 5 ms                        | 6 ms                    |
| P99 Latency               | **9 ms**                    | 19 ms                   |
| Max Latency               | **44 ms**                   | 96 ms                   |
| Requests per Second (RPS) | ~608.88                     | ~608.69                 |
| Failure Rate (`/error`)   | 100% (intentional)          | 100% (intentional)      |


**Analysis**  
- Both implementations achieved almost identical throughput (~609 RPS).  
- In this test, APIException’s **average latency was only +0.72 ms** higher than HTTPException (2.42 ms vs 2.00 ms).  
- **The P95 latencies** were nearly identical at 5 ms and 6 ms, while **the P99** and **maximum latencies** for APIException were slightly higher but still well within acceptable performance thresholds for APIs.
> `Important Notice:` `APIException` automatically logs exceptions, while FastAPI’s built-in `HTTPException` does not log them by default.
> Considering the extra **logging feature**, these performance results are **very strong**, showing that APIException delivers standardized error responses, cleaner exception handling, and logging capabilities **without sacrificing scalability**.


<figure style="margin: 0; text-align: center;">
  <img src="assets/APIException-vs-HTTPException–Latency-Comparison.png" alt="APIException vs HTTPException – Latency Comparison" style="display: block; margin: 0 auto;">
  <figcaption style="margin-top: 4px; font-style: italic; font-size: 0.9em;">
    HTTPException vs APIException – Latency Comparison
  </figcaption>
</figure>

Benchmark scripts and raw Locust reports are available in the [benchmark](https://github.com/akutayural/APIException/tree/main/benchmark) directory.

## 📚 Next Steps

Ready to integrate?
Check out:
- 🚀 [**Installation**](installation.md) — How to set up APIException.

- ⚡  [**Quick Start**](usage/quick_start.md) — Add it to your project in minutes.

- 🧩 [**Usage**](usage/response_model.md) — [Response models](usage/response_model.md), [custom codes](usage/custom_codes.md), and [fallback middleware](usage/fallback.md).

- 📚 [**Advanced**](advanced/swagger.md) — [Swagger integration](advanced/swagger.md), [logging](advanced/logging.md), debugging.

- 🔗 [**API Reference**](reference/api.md) — Full reference docs.

