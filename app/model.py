import uuid

from pydantic import BaseModel, Field, EmailStr, UUID4


class UserSchema(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    friends: list = []

    class Config:
        schema_extra = {
            "example": {
                "fullname": "Abdulazeez Abdulazeez Adeshina",
                "email": "abdulazeez@x.com",
                "password": "weakpassword",
                "friends": ["id1", "id2"]
            }
        }


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "abdulazeez@x.com",
                "password": "weakpassword"
            }
        }
