from pydantic import BaseModel,EmailStr,Field,model_validator
from enum import Enum
 

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"

class Utilisateur(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Role=Role.USER
    ispremium: bool = False   

    @model_validator(mode='after')
    def check_ispremium_for_user(self):
        # ispremium = values.ispremium
        if self.role == Role.ADMIN and self.ispremium:
            raise ValueError("Les admins ne peuvent pas avoir le champ 'ispremium' à True")
        return self
    
    class Config:
        schema_extra = {
            "example":{
                "username": "string",
                "email": "string",
                "password": "password",
                "role": "user",
                "ispremium": False

            }
        }