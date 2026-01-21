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

    return ResponseModel[UserModel](
        data=UserModel(id=user_id, username="John Doe"),
        description="User retrieved successfully.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)