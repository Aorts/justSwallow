from pydantic import BaseModel, Field
import datetime

from app.api.schemas import base, users, collections


class BasedCollectionOperationSchema(BaseModel):
    collection: collections.CollectionOutSchema
    owner: users.UserOutSchema
    amount: int
    status: str

    submitted_date: datetime.datetime
    updated_date: datetime.datetime
    completed_date: datetime.datetime | None


class CollectionOperationGeneratorSchema(BaseModel):
    amount: int = Field(..., example=10)
    generated_type: str = Field(..., example="normal-random")
    generated_class: str = Field(..., example="A")


class CollectionOperationSchema(base.BaseSchema, BasedCollectionOperationSchema):
    pass


class CollectionOperationOutSchema(base.BaseSchema, BasedCollectionOperationSchema):
    pass
