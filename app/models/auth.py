from pydantic import BaseModel, EmailStr, Field

# class UserCreate(BaseModel):
#     username: str = Field(..., min_length=1, max_length=50)
#     email: EmailStr
#     password: str = Field(..., min_length=6, max_length=72)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)

class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    ispremium: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
