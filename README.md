<p align="center">
  <img src="https://raw.githubusercontent.com/akutayural/APIException/main/assets/logo.png" alt="APIException Logo" width="450"/>
</p>
<p align="center"><b><i>Standardising FastAPI responses with clarity, consistency, and control.</i></b></p>

# APIException: Standardised Exception Handling for FastAPI

[![PyPI version](https://img.shields.io/pypi/v/apiexception?cacheSeconds=300)](https://pypi.org/project/apiexception/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://akutayural.github.io/APIException/)
[![Downloads](https://pepy.tech/badge/apiexception)](https://pepy.tech/project/apiexception)
[![Python Versions](https://img.shields.io/pypi/pyversions/apiexception.svg)](https://pypi.org/project/apiexception/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/badge/linting-ruff-%23ea580c?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/badge/packaging-uv-%234285F4?logo=python&logoColor=white)](https://github.com/astral-sh/uv)
[![Poetry](https://img.shields.io/badge/dependencies-poetry-%2360A5FA?logo=poetry&logoColor=white)](https://python-poetry.org/)
[![PyPI status](https://img.shields.io/pypi/status/apiexception?style=flat)](https://pypi.org/project/apiexception/)


**APIException** is a robust, production-ready Python library for FastAPI that simplifies exception handling and ensures consistent, well-structured API responses. Designed for developers who want to eliminate boilerplate error handling and improve Swagger/OpenAPI documentation, APIException makes your FastAPI projects cleaner and easier to maintain.

- 🔒 Consistent JSON responses for **both** success and errors.
- 📚 Beautiful Swagger/OpenAPI documentation with clear error cases.
- ⚙️ Customizable error codes with `BaseExceptionCode`.
- 🔗 Global fallback for unhandled server-side errors.
- 🗂️ Use with **multiple FastAPI apps**.
- 📜 Automatic logging of every exception detail.
- ✔️ Production-ready with unit test examples.

· [**View on PyPI**](https://pypi.org/project/APIException) 

· [**Full Documentation**](https://akutayural.github.io/APIException/)

Reading the [full documentation](https://akutayural.github.io/APIException/) is **highly recommended** — it’s clear, thorough, and helps you get started in minutes.

---

> [!IMPORTANT]
> **Actively maintained. Highly recommended.**
>
> **APIException** is actively maintained and used in real-world, production FastAPI services.
> It is designed to be **integrated as a library**, not copied piece by piece into projects.
>
> New features, bug fixes, performance improvements, and documentation updates
> are shipped continuously through releases.
> If you copy the implementation instead of installing the library,
> you will **miss future improvements**, fixes, and enhancements by design.
>
> If you find yourself copy-pasting error handling logic across services,
> this library exists to replace that pattern with something **cleaner, safer,
> and more sustainable over time**.
---

## 📦 Installation via pip

```bash
pip install apiexception
```

![pip-install-apiexception-1.gif](docs/assets/apiexception-indexPipInstallApiexception.gif)

---

 ## ⚡ Quickstart: How to Integrate APIException

**1️⃣ Plug and Play**

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from api_exception import (
    register_exception_handlers,
    APIException,
    BaseExceptionCode,
    ResponseModel,
    APIResponse,
)

app = FastAPI()
register_exception_handlers(app)  # uses ResponseModel by default


class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("USR-404", "User not found.", "The user ID does not exist.")


class UserModel(BaseModel):
    id: int = Field(..., example=1)
    username: str = Field(..., example="John Doe")


@app.get(
    "/user/{user_id}",
    response_model=ResponseModel[UserModel],
    responses=APIResponse.default(),
)
async def user(user_id: int):
    if user_id == 1:
        raise APIException(
            error_code=CustomExceptionCode.USER_NOT_FOUND,
            http_status_code=404,
        )
    
    if user_id == 3:
        a = 1
        b = 0
        c = a / b  # This will raise ZeroDivisionError and be caught by the global exception handler
        return c

    return ResponseModel[UserModel](
        data=UserModel(id=user_id, username="John Doe"),
        description="User retrieved successfully.",
    )

```


![_user_{user_id}.gif](/assets/apiexception-indexBasicUsage-1.gif)

![apiexception-indexApiExceptionLog.png](docs/advanced/exception_1.png)


⭐ **Enjoying APIException?**  
If this library saved you time or helped standardise your FastAPI responses,  
consider giving it a ⭐ on GitHub. It really helps the project grow.


---

 ## 🔍 Example: More Detailed Error Handling Example with Custom Codes

```python
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, Path, Request
from pydantic import BaseModel, Field
from api_exception import (
    APIException,
    BaseExceptionCode,
    ResponseModel,
    register_exception_handlers,
    APIResponse,
    logger,
    ResponseFormat
)

logger.setLevel("DEBUG")
app = FastAPI()


def my_extra_fields(request: Request, exc: Optional[BaseException]) -> Dict[str, Any]:
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

The above code demonstrates how to handle exceptions in FastAPI using the `APIException` library. 

When you run your FastAPI app and open **Swagger UI** (`/docs`),  
your endpoints will display **clean, predictable response schemas** like this below:

![_user_{user_id}.gif](/assets/apiexception-indexBasicUsage-1.gif)

![apiexception-indexApiExceptionLog.png](docs/advanced/exception_1.png)



For more examples, check it out in the [examples directory](https://github.com/akutayural/APIException/tree/main/examples).



---

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
---

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

---

In both `error` and the `success` cases, the response structure is **consistent**.

- In the example above, when the `user_id` is `1`, it raises an `APIException` with a custom `error_code`, the response is formatted according to the `ResponseModel` and it's logged **automatically** as shown below:

![apiexception-indexApiExceptionLog.png](docs/advanced/exception_1.png)

---

#### - Uncaught Exception API Response?

What if you forget to handle an exception such as in the **example** above?

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

![apiexception-indexApiExceptionLog.png](docs/advanced/exception_2.png)


**2️⃣ Raise an Exception**

```python
from api_exception import APIException, ExceptionCode, register_exception_handlers
from fastapi import FastAPI
app = FastAPI()

register_exception_handlers(app)

@app.get("/login")
async def login(username: str, password: str):
    if username != "admin" or password != "admin":
        raise APIException(
            error_code=ExceptionCode.AUTH_LOGIN_FAILED,
            http_status_code=401
        )
    return {"message": "Login successful!"}
```

---

**3️⃣ Use ResponseModel for Success Responses**

```python
from api_exception import ResponseModel, register_exception_handlers
from fastapi import FastAPI
app = FastAPI()

register_exception_handlers(app)

@app.get("/success")
async def success():
    return ResponseModel(
        data={"foo": "bar"},
        message="Everything went fine!"
    )
```

**_Response Model In Abstract:_**

![apiexception-responseModel.gif](assets/apiexception-responseModel.gif)


---

## 🧩 Custom Error Codes

Always extend BaseExceptionCode — don’t subclass ExceptionCode directly!

```python
from api_exception import BaseExceptionCode

class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("-404", "User not found.", "User does not exist.")
    INVALID_API_KEY = ("API-401", "Invalid API key.", "Key missing or invalid.")
```

And use it:

```python
from api_exception import APIException

raise APIException(
    error_code=CustomExceptionCode.USER_NOT_FOUND,
    http_status_code=404
)
```

---

## ⚙️ Override Default HTTP Status Codes

```python
from api_exception import set_default_http_codes

set_default_http_codes({
    "FAIL": 422,
    "WARNING": 202
})
```

---

## 🌐 Multiple Apps Support
```python
from fastapi import FastAPI
from api_exception import register_exception_handlers

mobile_app = FastAPI()
admin_app = FastAPI()
merchant_app = FastAPI()

register_exception_handlers(mobile_app)
register_exception_handlers(admin_app)
register_exception_handlers(merchant_app)
```

---

## 📝 Automatic Logging

Every APIException automatically logs:

- File name & line number

- Error code, status, message, description

Or use the built-in logger:

```python
from api_exception import logger

logger.info("Custom info log")
logger.error("Custom error log")
logger.setLevel("DEBUG")  # Set logging level
```

---

## Examples

### All in One Example Application
Below is a comprehensive example application demonstrating the capabilities of `api_exception`.  
This single file showcases how you can:

- Work with multiple FastAPI apps (**API**, **Mobile**, **Admin**) in the same project  
- Set different log levels based on the environment (e.g., **INFO** in dev, **ERROR** in prod)  
- Enable or disable **tracebacks** per application  
- Fully control logging behavior when raising `APIException` (**log** or **skip logging**)  
- Customize `DEFAULT_HTTP_CODES` to match your own status code mappings  
- Create and use **custom exception classes** with clean and consistent logging across the project  
- Use `APIResponse.custom()` and `APIResponse.default()` for flexible response structures  
- Demonstrate **RFC 7807 problem details** integration for standards-compliant error responses  

This example serves as a **one-stop reference** to see how `api_exception` can be integrated into a real-world project while keeping exception handling **consistent**, **configurable**, and **developer-friendly**.  

[**Click to see the example**](https://github.com/akutayural/APIException/blob/main/examples/production_level.py)


---
## ✅ Testing Example

```python
import unittest
from api_exception import APIException, ExceptionCode, ResponseModel

class TestAPIException(unittest.TestCase):
    def test_api_exception(self):
        exc = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        self.assertEqual(exc.status.value, "FAIL")

    def test_response_model(self):
        res = ResponseModel(data={"foo": "bar"})
        self.assertEqual(res.status.value, "SUCCESS")

if __name__ == "__main__":
    unittest.main()
```

**Run the Tests**
- To run the tests, you can use the following command in your terminal:

```bash
python -m unittest discover -s tests
```

---

## 🔗 Full Documentation

Find detailed guides and examples in the [official docs](https://akutayural.github.io/APIException/).

---
## 📊 Benchmark

We benchmarked **apiexception's** `APIException` against **FastAPI's** built-in `HTTPException` using **Locust** with **200** concurrent users over **2 minutes**.
This can be used as a foundation. Can be extended to include more detailed tests. 

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
  <img src="docs/assets/APIException-vs-HTTPException–Latency-Comparison.png" alt="APIException vs HTTPException – Latency Comparison" style="display: block; margin: 0 auto;">
  <figcaption style="margin-top: 4px; font-style: italic; font-size: 0.9em;">
    HTTPException vs APIException – Latency Comparison
  </figcaption>
</figure>

Benchmark scripts and raw Locust reports are available in the [benchmark](https://github.com/akutayural/APIException/tree/main/benchmark) directory.


---

## 📜 Changelog

Currently, the most stable and suggested version is v0.2.1

👉 [See full changelog](https://akutayural.github.io/APIException/changelog/)

---

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.
If you like this library and find it useful, don’t forget to give it a ⭐ on GitHub!

## Contact
If you have any questions or suggestions, please feel free to reach out at [ahmetkutayural.dev](https://ahmetkutayural.dev/#contact)
Don't forget to add your email to the contact form! 

---

## 📖 Learn More

📚 **Full APIException Documentation**  
https://akutayural.github.io/APIException/

🐍 **PyPI**  
https://pypi.org/project/apiexception/

💻 **Author **  
Ahmet Kutay Ural


---
⭐ **Used in real-world FastAPI projects**  
APIException is actively used in production systems and shared across the Python community.  
If you're using it in your project, a ⭐ on GitHub helps signal support and keeps development active.

---

## 🌍 Community & Recognition

- 📢 Featured in [**Python Weekly #710**](https://www.pythonweekly.com/p/python-weekly-issue-710-august-14-2025-3200567a10d37d87) 🎉  
- 🏆 Selected as one of the **Top Python Libraries of 2025** by [**Tryolabs**](https://tryolabs.com/blog/top-python-libraries-2025) 
- 🐍 Shared by [**PythonHub**](https://x.com/PythonHub/status/1957733129000472650) on X (Twitter)
- 🐦 Shared by [@tom_doerr](https://x.com/tom_doerr/status/1996308358916116964) on X (Twitter)
- ⭐ Gaining traction on GitHub with developers adopting it for real-world FastAPI projects.  
- 💬 Actively discussed and shared across the Python community.
