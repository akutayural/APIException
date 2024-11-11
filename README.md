# APIException

**APIException** is a customizable exception-handling library designed for Python and FastAPI applications, offering standardized error codes, messages, and HTTP status responses to improve error management and consistency across APIs.
[**View on PyPI**](https://pypi.org/project/APIException/0.1.0/)

## Installation

To install APIException, run:

```bash
pip install APIException
```
## Features

- **Standardized Error Handling**: APIException allows you to define a consistent format for error responses, making your API more predictable and easier to work with.

- **Customizable Error Codes and Messages**: Define custom error codes with specific messages and descriptions, making it easy to differentiate between various errors in your application.

- **HTTP Status Integration**: Set HTTP status codes alongside error messages, ensuring that API clients receive appropriate responses for different types of errors (e.g., 400 for client errors, 500 for server errors).

- **Automatic Logging**: Each exception raised includes automatic logging of details, such as the filename and line number, to help developers quickly locate issues.

- **Extensible Error Codes**: Extend the `ExceptionCode` class to add custom error codes unique to your application’s needs.

- **Compatibility with FastAPI**: APIException integrates seamlessly with FastAPI, allowing you to standardize error responses across your endpoints.

- **Descriptive Responses**: Provides detailed descriptions for errors, making it easier for developers and users to understand the context of an error.

- **Response Model Integration**: APIException includes a Pydantic `ResponseModel` for structuring successful responses, maintaining consistency across both success and error responses.

## Usage

### Step 1: Install the Package

Install the package via pip:

```bash
pip install APIException
```
### Step 2: Import and Use in Your FastAPI Project
The following example demonstrates how to use APIException in a FastAPI endpoint.

```python
from fastapi import FastAPI, HTTPException
from api_exception.exception import APIException
from custom_enum.enums import ExceptionCode, ExceptionStatus
from schemas.response_model import ResponseModel

app = FastAPI()

@app.get("/login")
async def login(username: str, password: str):
    # Simulate a login failure scenario
    if username != "admin" or password != "admin":
        # Raise an APIException for login failure
        raise APIException(
            error_code=ExceptionCode.AUTH_LOGIN_FAILED,
            http_status_code=401
        )
    # If login succeeds, return a success response
    return ResponseModel(data={"username": username})
```
### Customizing the APIException
You can customize the exception message, HTTP status code, and other details when raising an APIException.
```python
@app.get("/custom-error")
async def custom_error():
    # Example of a custom error with a custom message and description
    raise APIException(
        error_code=ExceptionCode.AUTH_LOGIN_FAILED,
        message="Custom error message.",
        description="Detailed description of the custom error.",
        http_status_code=403,
        status=ExceptionStatus.WARNING
    )
```


### Customizing the Exception Codes
To define custom error codes for specific needs in your application, extend the ExceptionCode class:
```python
from custom_enum.enums import BaseExceptionCode

class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("USR-404", "User not found.", "The specified user does not exist in the system.")
    INVALID_API_KEY = ("API-401", "Invalid API key provided.", "Please provide a valid API key.")


# Use the custom error code in an APIException
@app.get("/user/{user_id}")
async def get_user(user_id: int):
    # Simulate a scenario where the user is not found
    if user_id != 1:  # Assume only user with ID 1 exists
        raise APIException(
            error_code=CustomExceptionCode.USER_NOT_FOUND,
            http_status_code=404
        )
    return ResponseModel(data={"user_id": user_id, "name": "John Doe"})
```
### Response Model for Successful Responses
You can use ResponseModel for consistent structure in successful responses.
```python
@app.get("/success")
async def success():
    return ResponseModel(
        data={"message": "Operation was successful"},
        status=ExceptionStatus.SUCCESS,
        message="Success message",
    )
```

### Automatically Logging Exceptions

Each APIException raised automatically logs the exception details, including the location where the exception was raised. This is useful for debugging and monitoring your application.

### Handling Exceptions in FastAPI
To handle exceptions globally in FastAPI, you can use exception handlers.
```python
from fastapi.responses import JSONResponse
from fastapi import Request

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.http_status_code,
        content=exc.to_response()
    )
```
Now, any APIException raised in your application will be handled by this global exception handler, providing a consistent error format for all endpoints.

## Testing the APIException Library
You can test the library by writing unit tests. Here’s an example of how you might structure tests for the APIException library.
```python
import unittest
from api_exception.exception import APIException
from custom_enum.enums import ExceptionCode, ExceptionStatus
from schemas.response_model import ResponseModel

class TestAPIException(unittest.TestCase):

    def test_api_exception(self):
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        self.assertEqual(exception.error_code, "AUTH-1000")
        self.assertEqual(exception.message, "Incorrect username and password.")
        self.assertEqual(exception.description, "Failed authentication attempt.")
        self.assertEqual(exception.status, ExceptionStatus.FAIL)
        self.assertEqual(exception.http_status_code, 400)

        # Test the response dictionary
        response = exception.to_response()
        expected_response = {
            "error_code": "AUTH-1000",
            "status": "FAIL",
            "message": "Incorrect username and password.",
            "description": "Failed authentication attempt"
        }
        self.assertEqual(response, expected_response)

    def test_response_model(self):
        response = ResponseModel(data={"key": "value"})
        self.assertEqual(response.status, ExceptionStatus.SUCCESS)
        self.assertEqual(response.message, "Operation completed successfully.")
        self.assertIsNone(response.error_code)
        self.assertIsNone(response.description)
        self.assertEqual(response.data, {"key": "value"})

if __name__ == "__main__":
    unittest.main()
```
This test case verifies that the APIException class behaves as expected, including proper response formatting and attribute assignments.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue to improve this library. Follow the guidelines below:

	1.	Fork the repository.
	2.	Create a new branch.
	3.	Make your changes and ensure all tests pass.
	4.	Submit a pull request with a detailed description of the changes.

## Why Use APIException?

If you’re looking for a way to manage exception handling in a structured manner, especially if you want the backend to control the error messages displayed to end-users, then APIException is a great library for you. It provides an organized and extensible approach to managing error codes, messages, and descriptions directly from the backend, enhancing the overall API response consistency and user experience.

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.
If you like this library and find it useful, don’t forget to give it a ⭐ on GitHub!

## Contact
If you have any questions or suggestions, please feel free to reach out at [ahmetkutayural.dev](https://ahmetkutayural.dev/#contact)



