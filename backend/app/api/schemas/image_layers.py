from pydantic import BaseModel, Field
import datetime

from app.api.schemas import base, users, collections


class BasedImageLayerSchema(BaseModel):
    name: str = Field(..., example="background")
    description: str | None = Field(None, example="background image")
    order: int = Field(
        ..., ge=0, le=100, description="The order must be 0 to 100", example=0
    )
    required: bool = Field(..., example=True)


class ImageLayerCreatedSchema(BasedImageLayerSchema):
    collection_id: str = Field(..., example="conllection_id")


class ImageLayerUpdatedSchema(ImageLayerCreatedSchema):
    name: str | None
    description: str | None
    order: int | None
    collection_id: str | None


class ImageLayerSchema(base.BaseSchema, BasedImageLayerSchema):

    owner: users.UserOutSchema
    collection: collections.CollectionOutSchema
    created_date: datetime.datetime
    updated_date: datetime.datetime


class ImageLayerOutSchema(base.BaseSchema, BasedImageLayerSchema):

    owner: users.UserOutSchema
    collection: collections.CollectionOutSchema
