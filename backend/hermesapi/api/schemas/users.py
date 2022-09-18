from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
import datetime

from hermesapi.api.schemas import base


class UserSchema(base.BaseSchema):
    first_name: str
    last_name: str
    email: EmailStr
    created_date: datetime.datetime | None

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Foo",
                "last_name": "Bar",
                "email": "foo@email.mail",
            }
        }


class UserRegistrationSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Foo",
                "last_name": "Bar",
                "email": "foo@email.mail",
                "password": "password",
            }
        }


class UserUpdatedSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class UserOutSchema(base.BaseSchema, UserUpdatedSchema):
    pass
