from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

# Generic type for response data
DataT = TypeVar('DataT')


class RFC7807ResponseModel(BaseModel, Generic[DataT]):
    """
    Pydantic model compliant with RFC 7807 (Problem Details for HTTP APIs).

    This model standardizes error responses according to the RFC 7807 spec.
    It provides a consistent and interoperable format that includes all mandatory
    and optional fields specified by the standard.

    Attributes:
    -----------
    - type: Optional[`str`]
        A URI reference (can be a URL or a URN) for the type of error. Can point to documentation or specification.
    - title: `str`
        A short, human-readable summary of the error.
    - status: `int`
        The HTTP status code applicable to this error.
    - detail: Optional[`str`]
        A human-readable explanation specific to this occurrence of the problem.
    - instance: Optional[`str`]
        A URI reference that identifies the specific occurrence of the problem, e.g., the request path.

    Optional Extensions:
    --------------------
    - error_code: Optional[`str`]
        A custom internal error code for client-side parsing or analytics.
    """

    type: Optional[str] = Field(
        default=None,
        description="A URI reference (can be a URL or a URN) for the error type. Should point to a human-readable document or spec.",
        examples=["https://example.com/errors/invalid-input"]
    )
    title: str = Field(
        ...,
        description="A short, human-readable summary of the problem type.",
        examples=["Invalid Request", "Authentication Failed", "Permission Denied"]
    )
    status: int = Field(
        ...,
        description="The HTTP status code associated with this error.",
        examples=[400, 401, 403, 404, 422, 500]
    )
    detail: Optional[str] = Field(
        default=None,
        description="A human-readable explanation of the problem.",
        examples=[
            "The email field must be a valid email address.",
            "Your API key is missing or invalid.",
            "You do not have permission to access this resource."
        ]
    )
    instance: Optional[str] = Field(
        default=None,
        description="A URI that identifies the specific occurrence of the error, typically the request URI.",
        examples=["/users/create", "/auth/login"]
    )
