import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api_exception import (
    APIException,
    ExceptionCode,
    ExceptionStatus,
    ResponseModel,
    register_exception_handlers,
    set_default_http_codes,
    APIResponse,
)
from api_exception import ResponseFormat
from examples.fastapi_usage import CustomExceptionCode


class TestAPIException(unittest.TestCase):

    def test_api_exception_default(self):
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        self.assertEqual(exception.error_code, "AUTH-1000")
        self.assertEqual(exception.message, "Incorrect username and password.")
        self.assertEqual(exception.description, "Failed authentication attempt.")
        self.assertEqual(exception.status, ExceptionStatus.FAIL)
        self.assertEqual(exception.http_status_code, 400)

    def test_api_exception_custom_message(self):
        custom_message = "Custom error message."
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED, message=custom_message)
        self.assertEqual(exception.message, custom_message)

    def test_api_exception_custom_description(self):
        custom_description = "Custom description."
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED, description=custom_description)
        self.assertEqual(exception.description, custom_description)

    def test_api_exception_custom_status_code(self):
        custom_status_code = 403
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED, http_status_code=custom_status_code)
        self.assertEqual(exception.http_status_code, custom_status_code)

    def test_api_exception_to_response(self):
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        response = exception.to_response()
        self.assertEqual(response["error_code"], "AUTH-1000")
        self.assertEqual(response["status"], "FAIL")

    def test_api_exception_to_response_model(self):
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        response_model = exception.to_response_model()
        self.assertEqual(response_model.status, ExceptionStatus.FAIL)
        self.assertEqual(response_model.message, "Incorrect username and password.")

    def test_api_exception_to_rfc7807_response(self):
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        response_model = exception.to_rfc7807_response()
        self.assertEqual(response_model.detail, "Failed authentication attempt.")
        self.assertEqual(response_model.instance, "/login")
        self.assertEqual(response_model.title, "Incorrect username and password.")
        self.assertEqual(response_model.type, "https://example.com/problems/authentication-error")
        self.assertEqual(response_model.status, 400)

    def test_response_model_success(self):
        response = ResponseModel(data={"key": "value"})
        self.assertEqual(response.status, ExceptionStatus.SUCCESS)
        self.assertIsNone(response.error_code)
        self.assertEqual(response.data, {"key": "value"})

    def test_response_model_with_custom_message(self):
        response = ResponseModel(data={"key": "value"}, message="Custom success message.")
        self.assertEqual(response.message, "Custom success message.")

    def test_response_model_with_error(self):
        response = ResponseModel(
            data=None,
            status=ExceptionStatus.FAIL,
            message="An error occurred.",
            error_code="AUTH-1000",
            description="Failed authentication attempt"
        )
        self.assertEqual(response.status, ExceptionStatus.FAIL)
        self.assertEqual(response.message, "An error occurred.")
        self.assertEqual(response.error_code, "AUTH-1000")

    def test_set_default_http_codes(self):
        new_map = {ExceptionStatus.FAIL: 500}
        set_default_http_codes(new_map)
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        self.assertEqual(exception.http_status_code, 400)
        exception2 = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED, http_status_code=None)
        self.assertEqual(exception2.http_status_code, 500)

    def test_register_exception_handlers_with_fastapi(self):
        app = FastAPI()
        register_exception_handlers(app)

        @app.get("/test")
        def test_endpoint():
            raise APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)

        client = TestClient(app)
        response = client.get("/test")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_code"], "AUTH-1000")
        self.assertEqual(response.json()["status"], "FAIL")

    def test_register_exception_handlers_raw_response(self):
        app = FastAPI()
        register_exception_handlers(app, response_format=ResponseFormat.RESPONSE_DICTIONARY)

        @app.get("/test-raw")
        def test_endpoint():
            raise APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)

        client = TestClient(app)
        response = client.get("/test-raw")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_code"], "AUTH-1000")
        self.assertIn("message", response.json())

    def test_register_exception_handlers_rfc7807_response(self):
        app = FastAPI()
        register_exception_handlers(app, response_format=ResponseFormat.RFC7807)

        @app.get("/test-rfc7807")
        def test_endpoint():
            raise APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)

        client = TestClient(app)
        response = client.get("/test-rfc7807")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["type"], "https://example.com/problems/authentication-error")
        self.assertEqual(response.json()["instance"], "/login")
        self.assertEqual(response.json()["title"], "Incorrect username and password.")
        self.assertEqual(response.json()["detail"], "Failed authentication attempt.")
        self.assertEqual(response.json()["status"], 400)
        self.assertEqual(response.headers.get("content-type", None), "application/problem+json")

    def test_register_exception_handlers_model_response(self):
        app = FastAPI()
        register_exception_handlers(app, response_format=ResponseFormat.RESPONSE_MODEL)

        @app.get("/test-response")
        def test_endpoint():
            raise APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)

        client = TestClient(app)
        response = client.get("/test-response")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_code"], "AUTH-1000")

    def test_openapi(self):
        app = FastAPI()
        register_exception_handlers(app, response_format=ResponseFormat.RESPONSE_MODEL)

        @app.get("/test-openapi", responses=APIResponse.rfc7807(
            (401, CustomExceptionCode.INVALID_API_KEY, "https://example.com/errors/unauthorized", "/account/info"),
            (403, CustomExceptionCode.PERMISSION_DENIED, "https://example.com/errors/forbidden", "/admin/panel"),
            (422, CustomExceptionCode.VALIDATION_ERROR, "https://example.com/errors/unprocessable-entity",
             "/users/create")
        ))
        def test_endpoint():
            raise APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)

        expected = {
            "200": {
                "description": "Successful Response",
                "content": {
                    "application/json": {
                        "schema": {}
                    }
                }
            },
            "401": {
                "description": "Status: 401 - API-401",
                "content": {
                    "application/problem+json": {
                        "example": {
                            "type": "https://example.com/errors/unauthorized",
                            "title": "Invalid API key.",
                            "status": 401,
                            "detail": "Provide a valid API key.",
                            "instance": "/account/info"
                        }
                    }
                }
            },
            "403": {
                "description": "Status: 403 - PERM-403",
                "content": {
                    "application/problem+json": {
                        "example": {
                            "type": "https://example.com/errors/forbidden",
                            "title": "Permission denied.",
                            "status": 403,
                            "detail": "Access to this resource is forbidden.",
                            "instance": "/admin/panel"
                        }
                    }
                }
            },
            "422": {
                "description": "Status: 422 - VAL-422",
                "content": {
                    "application/problem+json": {
                        "example": {
                            "type": "https://example.com/errors/unprocessable-entity",
                            "title": "Validation Error",
                            "status": 422,
                            "detail": "Input validation failed.",
                            "instance": "/users/create"
                        }
                    }
                }
            }
        }
        client = TestClient(app)
        response = client.get("/openapi.json").json()
        responses = response.get("paths").get("/test-openapi").get("get").get("responses")

        for code, expected_response in expected.items():
            with self.subTest(code=code):
                self.assertIn(code, responses)
                actual = responses[code]

                # Check description
                self.assertEqual(actual["description"], expected_response["description"])

                # Check example or schema
                expected_content = expected_response["content"]["application/json"] if "application/json" in expected_response["content"] else expected_response["content"]["application/problem+json"]
                actual_content = actual["content"]["application/json"] if "application/json" in actual["content"] else actual["content"]["application/problem+json"]

                if "schema" in expected_content:
                    self.assertIn("schema", actual_content)
                    self.assertEqual(actual_content["schema"], expected_content["schema"])
                else:
                    self.assertIn("example", actual_content)
                    for key, val in expected_content["example"].items():
                        self.assertIn(key, actual_content["example"])
                        self.assertEqual(actual_content["example"][key], val)

    def test_fallback_handler(self):
        app = FastAPI()
        register_exception_handlers(app)

        @app.get("/crash")
        async def crash():
            raise ValueError("Some unexpected error")

        client = TestClient(app)
        response = client.get("/crash")
        self.assertEqual(response.status_code, 500)
        body = response.json()
        self.assertEqual(body["status"], "FAIL")
        self.assertEqual(body["error_code"], "ISE-500")
        self.assertIn("wrong", body["message"])
        self.assertIn("An unexpected error occurred", body["description"])


if __name__ == "__main__":
    unittest.main()