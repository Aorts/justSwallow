from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
import io

from app import models
from .. import schemas
from .. import core

router = APIRouter(prefix="/component-images", tags=["component-images"])


# @router.post(
#     "",
#     response_model_by_alias=False,
#     response_model=schemas.component_images.ComponentImageSchema,
# )
# def create(
#     component_image: schemas.component_images.ComponentImageCreatedSchema,
#     current_user: models.User = Depends(core.deps.get_current_user),
# ):
#     db_image_layer = models.ImageLayer.objects(
#         id=component_images.image_layer_id,
#         owner=current_user,
#     ).first()
#     db_component_image = models.ComponentImage.objects(
#         name=component_image.name,
#         owner=current_user,
#         image_layer=db_image_layer,
#     ).first()
#     if db_component_image:
#         raise HTTPException(
#             status_code=409,
#             detail=f"There are already component_image {component_image.name} in system",
#         )

#     data = component_image.dict()
#     data.pop("image_layer_id")
#     db_component_image = models.ComponentImage(**data)
#     db_component_image.owner = current_user
#     db_component_image.save()

#     return db_component_image


@router.get(
    "",
    response_model_by_alias=False,
    response_model=list[schemas.component_images.ComponentImageSchema],
)
def list_component_images(
    image_layer_id: str = None,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_component_images = []
    if image_layer_id:
        image_layer = models.ImageLayer.objects(
            id=image_layer_id, owner=current_user
        ).first()
        db_component_images = models.ComponentImage.objects(
            owner=current_user, image_layer=image_layer
        )
    else:
        db_component_images = models.ComponentImage.objects(owner=current_user)

    component_images = []
    for c_image in db_component_images:
        component_images.append(c_image)
    return component_images


@router.get(
    "/{component_image_id}",
    response_model_by_alias=False,
    response_model=schemas.component_images.ComponentImageSchema,
)
def get(
    component_image_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_component_image = models.ComponentImage.objects(
        id=component_image_id, owner=current_user
    ).first()
    if not db_component_image:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {component_image_id} component_image in system",
        )

    return db_component_image


@router.put(
    "/{component_image_id}",
    response_model_by_alias=False,
    response_model=schemas.component_images.ComponentImageSchema,
)
def update(
    component_image_id: str,
    component_image: schemas.component_images.ComponentImageUpdatedSchema,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_component_image = models.ComponentImage.objects(
        id=component_image_id, owner=current_user
    ).first()
    if not db_component_image:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {component_image_id} component_image in system",
        )
    set_dict = {
        f"set__{k}": v for k, v in component_image.dict().items() if v is not None
    }
    db_component_image.update(**set_dict)
    db_component_image.reload()

    return db_component_image


@router.delete(
    "/{component_image_id}",
    response_model_by_alias=False,
    response_model=schemas.component_images.ComponentImageSchema,
)
def delete(
    component_image_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_component_image = models.ComponentImage.objects(
        id=component_image_id, owner=current_user
    ).first()
    if not db_component_image:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {component_image_id} component_image in system",
        )

    data = schemas.component_images.ComponentImageSchema.from_orm(db_component_image)
    db_component_image.image.delete()
    db_component_image.delete()

    return data


@router.get(
    "/{component_image_id}/download/{filename}",
)
def download(
    component_image_id: str,
    filename: str,
    # current_user: models.User = Depends(core.deps.get_current_user),
):
    component_image = models.ComponentImage.objects(
        id=component_image_id,
        # owner=current_user
    ).first()
    if not component_image:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {component_image_id} component_image in system",
        )

    img = component_image.image.read()
    content_type = component_image.image.content_type
    return Response(content=img, media_type=content_type)
