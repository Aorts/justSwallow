from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
import asyncio
import io
from pydantic import parse_obj_as


from hermesapi import models
from .. import schemas
from .. import core

router = APIRouter(prefix="/image-layers", tags=["image-layers"])


@router.post(
    "",
    response_model_by_alias=False,
    response_model=schemas.image_layers.ImageLayerSchema,
)
def create(
    image_layer: schemas.image_layers.ImageLayerCreatedSchema,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    collection = models.Collection.objects(
        id=image_layer.collection_id, owner=current_user
    ).first()
    if not collection:
        raise HTTPException(
            status_code=409,
            detail=f"There are no collection {collection.id} in system",
        )

    db_image_layer = models.ImageLayer.objects(
        name=image_layer.name,
        collection=collection,
    ).first()
    if db_image_layer:
        raise HTTPException(
            status_code=409,
            detail=f"There are already image_layer {image_layer.name} in system",
        )

    data = image_layer.dict()
    data.pop("collection_id")
    db_image_layer = models.ImageLayer(**data)
    db_image_layer.collection = collection
    db_image_layer.owner = current_user
    db_image_layer.save()

    return db_image_layer


@router.get(
    "",
    response_model_by_alias=False,
    response_model=list[schemas.image_layers.ImageLayerSchema],
)
def list_image_layers(
    collection_id: str = None,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_image_layers = []
    if collection_id:
        collection = models.Collection.objects(
            id=collection_id, owner=current_user
        ).first()
        if collection:
            db_image_layers = models.ImageLayer.objects(
                owner=current_user, collection=collection
            )
    else:
        db_image_layers = models.ImageLayer.objects(owner=current_user)

    image_layers = list(db_image_layers)
    image_layers.sort(key=lambda il: il.order)

    return image_layers


@router.get(
    "/{image_layer_id}",
    response_model_by_alias=False,
    response_model=schemas.image_layers.ImageLayerSchema,
)
def get(
    image_layer_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_image_layer = models.ImageLayer.objects(
        id=image_layer_id, owner=current_user
    ).first()
    if not db_image_layer:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {image_layer_id} image_layer in system",
        )

    return db_image_layer


@router.put(
    "/{image_layer_id}",
    response_model_by_alias=False,
    response_model=schemas.image_layers.ImageLayerSchema,
)
def update(
    image_layer_id: str,
    image_layer: schemas.image_layers.ImageLayerUpdatedSchema,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_image_layer = models.ImageLayer.objects(
        id=image_layer_id, owner=current_user
    ).first()
    if not db_image_layer:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {image_layer_id} image_layer in system",
        )
    set_dict = {f"set__{k}": v for k, v in image_layer.dict().items() if v is not None}
    db_image_layer.update(**set_dict)
    db_image_layer.reload()

    return db_image_layer


@router.delete(
    "/{image_layer_id}",
    response_model_by_alias=False,
    response_model=schemas.image_layers.ImageLayerSchema,
)
def delete(
    image_layer_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):

    db_image_layer = models.ImageLayer.objects(
        id=image_layer_id, owner=current_user
    ).first()

    if not db_image_layer:
        raise HTTPException(
            status_code=404,
            detail=f"Image layer {image_layer.id} not found in system",
        )

    db_component_images = models.ComponentImage.objects(
        owner=current_user,
        image_layer=db_image_layer,
    )

    for component_image in db_component_images:
        component_image.image.delete()
        component_image.delete()

    data = schemas.image_layers.ImageLayerSchema.from_orm(db_image_layer)
    db_image_layer.delete()

    print(data)

    return data


@router.post(
    "/{image_layer_id}/upload",
    response_model_by_alias=False,
    response_model=list[schemas.component_images.ComponentImageSchema],
)
def upload_component_images(
    image_layer_id: str,
    component_class: str = Form("A", description="Component Class"),
    rarity_weight: float = Form(0, description="Rarity Weight"),
    files: list[UploadFile] = File(..., description="Multiple files as UploadFile"),
    current_user: models.User = Depends(core.deps.get_current_user),
):

    db_image_layer = models.ImageLayer.objects(
        id=image_layer_id, owner=current_user
    ).first()
    if not db_image_layer:
        raise HTTPException(
            status_code=404,
            detail=f"Image layer {image_layer.id} not found in system",
        )

    component_images = []
    for file in files:
        name = file.filename[: file.filename.rfind(".")]
        component_image = models.ComponentImage(
            name=name,
            owner=current_user,
            component_class=component_class,
            rarity_weight=rarity_weight,
            image_layer=db_image_layer,
        )

        data = asyncio.run(file.read())
        image_io = io.BytesIO(data)
        component_image.image.put(
            image_io,
            content_type=file.content_type,
            filename=file.filename,
        )

        component_image.save()
        component_images.append(component_image)

    return component_images


@router.delete(
    "/{image_layer_id}/delete",
    response_model_by_alias=False,
    response_model=list[schemas.component_images.ComponentImageSchema],
)
def delete_component_images(
    image_layer_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):

    db_image_layer = models.ImageLayer.objects(
        id=image_layer_id, owner=current_user
    ).first()
    if not db_image_layer:
        raise HTTPException(
            status_code=404,
            detail=f"Image layer {image_layer.id} not found in system",
        )

    db_component_images = models.ComponentImage.objects(
        owner=current_user,
        image_layer=db_image_layer,
    )

    data = parse_obj_as(
        list[schemas.component_images.ComponentImageSchema], list(db_component_images)
    )

    for component_image in db_component_images:
        component_image.image.delete()
        component_image.delete()

    return data
