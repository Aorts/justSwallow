from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
import datetime

from app.api.schemas import base


class UserSchema(base.BaseSchema):
    first_name: str
    last_name: str
    email: EmailStr
    created_date: datetime.datetime | None


class UserRegistrationSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserUpdatedSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class UserOutSchema(base.BaseSchema, UserUpdatedSchema):
    pass
