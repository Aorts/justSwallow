from pydantic import BaseModel, Field
import datetime

from app.api.schemas import base, users


class BasedCollectionSchema(BaseModel):
    name: str = Field(..., example="The grestest art work")
    description: str | None = Field(
        None, example="This collection got inspired by mathematics"
    )
    external_url_template: str | None = Field(
        None, example="http://localhost:8081/v1/art-images/{id}/{filename}"
    )
    metadata_format: str = Field("opensea", example="opensea")
    file_host: str | None = Field("pinata", example="pinata")

class CollectionCreatedSchema(BasedCollectionSchema):
    file_api_key: str | None = Field(None, example="")
    file_api_secret: str | None = Field(None, example="")


class CollectionUpdatedSchema(CollectionCreatedSchema):
    name: str | None
    metadata_format: str | None


class CollectionSchema(base.BaseSchema, BasedCollectionSchema):
    file_token_cid: str | None
    file_json_token_cid: str | None
    generated_trait: int | None
    image_amount: int | None = Field(None, example=0)

    created_date: datetime.datetime
    updated_date: datetime.datetime


class CollectionOutSchema(base.BaseSchema, BasedCollectionSchema):
    pass


class CollectionFileHostSchema(BaseModel):
    file_host: str | None = Field(None, example="pinata")
    file_api_key: str | None = Field(None, example="")
    file_api_secret: str | None = Field(None, example="")
