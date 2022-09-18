from pydantic import BaseModel, Field
import datetime

from hermesapi.api.schemas import base, users, collections


class BasedArtImageSchema(BaseModel):
    name: str = Field(..., example="#00001")
    description: str | None = Field(..., example="very grate art image")


class ArtImageUpdatedSchema(BasedArtImageSchema):
    name: str | None
    description: str | None


class ArtImageSchema(base.BaseSchema, BasedArtImageSchema):
    uri: str | None
    url: str | None

    metadata: dict | None = Field(..., example="{}")
    rarity: float = Field(..., description="", example=0)
    rarity_percent: float = Field(..., description="", example=0)
    image_class: str = Field(..., description="", example="A")
    trait_rarity: dict | None = Field(..., example="{}")
    filename: str | None = Field(..., example="filename.png")

    owner: users.UserOutSchema
    collection: collections.CollectionOutSchema
    created_date: datetime.datetime


class ArtImageGallerySchema(BaseModel):
    number: int | None
    skip: int = 0
    limit: int = 0
    images: list[ArtImageSchema]


class ArtImageOutSchema(base.BaseSchema, BasedArtImageSchema):
    metadata: dict | None = Field(..., example="{}")
    rarity: float = Field(..., description="The rarity must be 0 to 100", example=0)
    rarity_percent: float = Field(..., description="", example=0)
    image_class: str = Field(..., description="", example="A")
    trait_rarity: dict | None = Field(..., example="{}")
    filename: str | None = Field(..., example="filename.png")

    owner: users.UserOutSchema
    collection: collections.CollectionOutSchema
    created_date: datetime.datetime
