from pydantic import BaseModel


class TokenResponseModel(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequestModel(BaseModel):
    email: str
    password: str
