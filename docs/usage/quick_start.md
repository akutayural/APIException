# ⚡ Quick Start

Get up and running with APIException in just a few minutes!

## ✅ Install the Package

If you haven't done it yet, Let's first start by installing APIException from PyPI:
```bash
pip install apiexception
```

## ✅ Register Exception Handlers
Add the register_exception_handlers to your FastAPI app to automatically handle and standardize your responses:

```python
from api_exception import register_exception_handlers
from fastapi import FastAPI

app = FastAPI()

register_exception_handlers(app=app)
```
That’s it!
Your API now returns consistent success & error responses, and unexpected server errors are automatically logged with a clear JSON output.

## ✅ Example Endpoint

Here’s a minimal example:

```python
from fastapi import FastAPI, Path
from pydantic import BaseModel, Field
from api_exception import APIException, register_exception_handlers, ResponseModel, APIResponse, BaseExceptionCode

app = FastAPI()

# Register exception handlers globally to have the consistent
# error handling and response structure
register_exception_handlers(app=app)


# Create the validation model for your response
class UserResponse(BaseModel):
    id: int = Field(..., example=1, description="Unique identifier of the user")
    username: str = Field(..., example="Micheal Alice", description="Username or full name of the user")


# Define your custom exception codes extending BaseExceptionCode
class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("USR-404", "User not found.", "The user ID does not exist.")


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
    data = UserResponse(id=1, username="John Doe")
    return ResponseModel[UserResponse](
        data=data,
        description="User found and returned."
    )
```
The below video demonstrates what actually the example code does.

<video autoplay loop muted playsinline width="900">
  <source src="../apiexception-indexBasicUsage.mp4" type="video/mp4">
</video>



`Swagger UI` will be well structured. 

## 📚 Next

✔️ Want to learn how to customize your responses?  
Check out
[🧩 Usage](../usage/response_model.md) for [response models](../usage/response_model.md), [custom exception codes](../usage/custom_codes.md), and [fallback middleware](../usage/fallback.md).

✔️ Need to fine-tune Swagger docs?  
See [📚 Advanced](../advanced/swagger.md) for better [documentation](../advanced/swagger.md) & [logging tips](../advanced/logging.md).