from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
import io

from app import models
from .. import schemas
from .. import core

router = APIRouter(prefix="/art-images", tags=["art-images"])


@router.get(
    "",
    response_model_by_alias=False,
    response_model=list[schemas.art_images.ArtImageSchema],
)
def list_art_images(
    collection_id: str,
    start: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(core.deps.get_current_user),
):

    db_collection = models.Collection.objects(id=collection_id).first()
    if not db_collection:
        return []

    db_art_images = (
        models.ArtImage.objects(collection=db_collection)
        .order_by("name")
        .skip(start)
        .limit(limit)
    )
    return list(db_art_images)


@router.delete(
    "",
)
def delete_art_images(
    collection_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):

    db_collection = models.Collection.objects(id=collection_id).first()
    if not db_collection:
        return []

    db_art_images = models.ArtImage.objects(collection=db_collection)
    data = list(db_art_images).copy()

    for ai in db_art_images:
        ai.image.delete()
        ai.delete()

    return


@router.get(
    "/{art_image_id}",
    response_model_by_alias=False,
    response_model=schemas.art_images.ArtImageSchema,
)
def get(
    art_image_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_art_image = models.ArtImage.objects(id=art_image_id).first()
    if not db_art_image:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {art_image_id} art_image in system",
        )

    return db_art_image


@router.put(
    "/{art_image_id}",
    response_model_by_alias=False,
    response_model=schemas.art_images.ArtImageSchema,
)
def update(
    art_image_id: str,
    art_image: schemas.art_images.ArtImageUpdatedSchema,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_art_image = models.ArtImage.objects(id=art_image_id, owner=current_user).first()
    if not db_art_image:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {art_image_id} art_image in system",
        )
    set_dict = {f"set__{k}": v for k, v in art_image.dict().items() if v is not None}
    db_art_image.update(**set_dict)
    db_art_image.reload()

    return db_art_image


@router.delete(
    "/{art_image_id}",
    response_model_by_alias=False,
    response_model=schemas.art_images.ArtImageSchema,
)
def delete(
    art_image_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_art_image = models.ArtImage.objects(id=art_image_id).first()
    if not db_art_image:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {art_image_id} art_image in system",
        )

    data = schemas.art_images.ArtImageSchema.from_orm(db_art_image)
    db_art_image.image.delete()
    db_art_image.delete()

    return data


@router.get(
    "/{art_image_id}/download/{filename}",
)
def download(art_image_id: str, filename: str):
    art_image = models.ArtImage.objects(id=art_image_id).first()
    if not art_image:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {art_image_id} art_image in system",
        )

    img = art_image.image.read()
    content_type = art_image.image.content_type
    return Response(content=img, media_type=content_type)
