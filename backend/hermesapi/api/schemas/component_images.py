from pydantic import BaseModel, Field
import datetime

from hermesapi.api.schemas import base, users, image_layers


class BasedComponentImageSchema(BaseModel):
    name: str = Field(..., example="blue")
    description: str | None = Field(..., example="blue eye came from the sky")
    component_class: str = Field("A", example="A")
    rarity_weight: float = Field(0, example="0")


class ComponentImageCreatedSchema(BasedComponentImageSchema):
    image_layer_id: str


class ComponentImageUpdatedSchema(ComponentImageCreatedSchema):
    name: str | None
    rarity: int | None
    image_layer_id: str | None


class ComponentImageSchema(base.BaseSchema, BasedComponentImageSchema):
    filename: str | None
    uri: str | None
    url: str | None
    owner: users.UserOutSchema
    image_layer: image_layers.ImageLayerOutSchema
    created_date: datetime.datetime
    updated_date: datetime.datetime

    rarity: float = Field(0, description="rarity", example=0)
    rarity_percent: float = Field(0, description="rarity percent", example=0)
    generated_number: int = Field(0, description="generated number:", example=0)


class ComponentImageOutSchema(base.BaseSchema, BasedComponentImageSchema):
    filename: str | None
    uri: str | None
    url: str | None
    owner: users.UserOutSchema
    image_layer: image_layers.ImageLayerOutSchema

    rarity: float = Field(..., description="rarity", example=0)
    rarity_percent: float = Field(..., description="rarity percent", example=0)
    generated_number: int = Field(0, description="generated number:", example=0)
