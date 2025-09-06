from api_exception import APIException, ExceptionCode


def basic_example():
    try:
        # Simulate a condition where an exception should be raised
        raise APIException(
            error_code=ExceptionCode.AUTH_LOGIN_FAILED,
            message="Custom login failure message.",
            description="This example shows how to use APIException for a login failure."
        )
    except APIException as e:
        # Print the structured response
        print("APIException raised:")
        print("Raw dict:", e.to_response())


if __name__ == "__main__":
    basic_example()