# 🔗 API Reference

This page lists the main classes, utilities, and helpers you’ll use when working with APIException in your FastAPI project.

Use this as a quick lookup when you want to check arguments, defaults, or core methods.

---

## ✅ Available Exports

### ResponseModel
**📌 What it is:**

A generic, strongly-typed Pydantic model that standardizes all API responses.

- ✅ Where to import:

```python
from api_exception import ResponseModel
```

- ✅ Key Fields:

	•	`data`: your payload

	•	`status`: SUCCESS, WARNING, FAIL

	•	`message`: short summary

	•	`error_code`: only set for failures

	•	`description`: extra context for debugging

`message` and `status` are **Required fields** and the rest is **Optional**. 

---

### APIException
**📌 What it is:**

Your main custom exception class — use this to raise predictable, documented API errors.

- ✅ Where to import:

```python
from api_exception import APIException
```

- ✅ Key Args:

	•	`error_code`: your BaseExceptionCode enum

	•	`http_status_code`: maps to HTTP status


---

### BaseExceptionCode
**📌 What it is:**

Base class for defining your custom business exception codes.

- ✅ Where to import:

```python
from api_exception import BaseExceptionCode
```

---

### APIResponse
**📌 What it is:**
A helper to document your Swagger/OpenAPI responses easily.

- ✅ Where to import:

```python
from api_exception import APIResponse
```

- ✅ Usage:

	•	`APIResponse.default()` → adds standard 400–500 errors.

	•	`APIResponse.custom()` → add your own error codes with status.


---

### register_exception_handlers
**📌 What it is:**

Sets up global handlers to catch APIException and unexpected errors.

- ✅ Where to import:

```python
from api_exception import register_exception_handlers
```

It's detailed in the [Register Exception Handlers](../usage/register_exception_handlers.md) section.

## ⚡ Example

Here’s how a typical setup might look:

```python
from api_exception import (
    APIException,
    BaseExceptionCode,
    ResponseModel,
    APIResponse,
    register_exception_handlers
)
```


## 📚 Next

✔️ Haven’t seen how to integrate yet?  
Go to [🚀 Installation](../installation.md)

✔️ Want a quick end-to-end setup?  
Check out [⚡ Quick Start](../usage/quick_start.md)

✔️ See how to extend this with your own codes:  
Read [🗂️ Custom Exception Codes](../usage/custom_codes.md)
