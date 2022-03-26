import enum
import uuid

from pydantic import BaseModel, Field, EmailStr, UUID4


class UserSchema(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    surname: str = Field(...)
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    profile_pic_url : str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "id" : "000000000-0000000000-00000000",
                "fullname": "Abdulazeez Abdulazeez Adeshina",
                "email": "abdulazeez@x.com",
                "password": "weakpassword",
                "profile_pic_url": "https://xxxxxx"
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


class FriendshipRequest(BaseModel):
    profile_id: UUID4
    target_profile_id: UUID4


class Relationship(BaseModel):
    FRIEND: bool # True meaning friends
    user_id: UUID4
    friend_id: UUID4

    class Config:
        schema_extra = {
            "example": {
                "FRIEND": "TRUE",
                "user_id": "000000000-0000000000-00000000",
                "friend_id": "000000000-0000000000-00000000",
            }
        }
