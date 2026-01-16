from pydantic import BaseModel


class LoginRequest(BaseModel):
    employee_id: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    name: str
    role: str
    branch_id: str
