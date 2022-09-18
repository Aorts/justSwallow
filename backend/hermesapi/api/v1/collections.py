from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response

import datetime
import pathlib

from hermesapi import models, config
from .. import schemas
from .. import core

router = APIRouter(prefix="/collections", tags=["collections"])


@router.post(
    "",
    response_model_by_alias=False,
    response_model=schemas.collections.CollectionSchema,
)
def create(
    collection: schemas.collections.CollectionCreatedSchema,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_collection = models.Collection.objects(
        name=collection.name, owner=current_user
    ).first()
    if db_collection:
        raise HTTPException(
            status_code=409,
            detail=f"There are already collection {collection.name} in system",
        )

    data = collection.dict()
    data.pop("file_api_key")
    data.pop("file_api_secret")

    db_collection = models.Collection(**data)
    db_collection.owner = current_user
    db_collection.save()

    if collection.file_api_key:
        db_collection.file_api_key = db_collection.encrypt_data(collection.file_api_key)
    if collection.file_api_secret:
        db_collection.file_api_secret = db_collection.encrypt_data(
            collection.file_api_secret
        )
    db_collection.save()

    return db_collection


@router.get(
    "/{collection_id}/art_images/{art_file_name}", response_model_by_alias=False
)
def get_art_images(collection_id: str, art_file_name: str):
    db_collection = models.Collection.objects(id=collection_id).first()
    if not db_collection:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {collection_id} collection in system",
        )

    db_art_image = models.ArtImage.objects(
        collection=db_collection, name=f"{art_file_name}.png"
    ).first()
    if not db_art_image:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {art_file_name} art_image in system",
        )
    data = {
        "file_id": str(db_art_image.id),
        "file_name": db_art_image.name,
        "download": f"localhost:8081/v1/art-images/{db_art_image.id}/download/{art_file_name}.png",
    }
    return data


@router.get(
    "",
    response_model_by_alias=False,
    response_model=list[schemas.collections.CollectionSchema],
)
def list_collections(
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_collections = models.Collection.objects(owner=current_user)

    return list(db_collections)


@router.get(
    "/{collection_id}",
    response_model_by_alias=False,
    response_model=schemas.collections.CollectionSchema,
)
def get(
    collection_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_collection = models.Collection.objects(
        id=collection_id, owner=current_user
    ).first()
    if not db_collection:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {collection_id} collection in system",
        )

    return db_collection


@router.put(
    "/{collection_id}",
    response_model_by_alias=False,
    response_model=schemas.collections.CollectionSchema,
)
def update(
    collection_id: str,
    collection: schemas.collections.CollectionUpdatedSchema,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_collection = models.Collection.objects(
        id=collection_id, owner=current_user
    ).first()
    if not db_collection:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {collection_id} collection in system",
        )
    set_dict = {
        f"set__{k}": v
        for k, v in collection.dict().items()
        if v is not None and k not in ["file_api_key", "file_api_secret"]
    }
    db_collection.update(**set_dict)

    db_collection.reload()

    if collection.file_api_key:
        db_collection.file_api_key = db_collection.encrypt_data(collection.file_api_key)
    if collection.file_api_secret:
        db_collection.file_api_secret = db_collection.encrypt_data(
            collection.file_api_secret
        )

    db_collection.save()

    return db_collection


@router.delete(
    "/{collection_id}",
    response_model_by_alias=False,
    response_model=schemas.collections.CollectionSchema,
)
def delete(
    collection_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_collection = models.Collection.objects(
        id=collection_id, owner=current_user
    ).first()
    if not db_collection:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {collection_id} collection in system",
        )

    data = schemas.collections.CollectionSchema.from_orm(db_collection)

    db_image_layers = models.ImageLayer.objects(collection=collection)
    db_component_images = models.ComponentImage.objects(
        image_layser__in=db_image_layers
    )
    db_art_images = models.ArtImage.objects(collection=collection)

    for ai in db_art_images:
        ai.image.delete()
        ai.delete()

    for ci in db_component_images:
        ci.image.delete()
        ci.delete()

    for il in db_image_layers:
        il.image.delete()
        il.delete()

    db_collection.delete()

    return data


@router.put(
    "/{collection_id}/file_host",
    response_model_by_alias=False,
    response_model=schemas.collections.CollectionSchema,
)
def update_file_host(
    collection_id: str,
    collection: schemas.collections.CollectionFileHostSchema,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_collection = models.Collection.objects(
        id=collection_id, owner=current_user
    ).first()
    if not db_collection:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {collection_id} collection in system",
        )
    set_dict = {
        f"set__{k}": v
        for k, v in collection.dict().items()
        if v is not None and k not in ["file_api_key", "file_api_secret"]
    }

    db_collection.update(**set_dict)

    db_collection.reload()

    if collection.file_api_key:
        db_collection.file_api_key = db_collection.encrypt_data(collection.file_api_key)
    if collection.file_api_secret:
        db_collection.file_api_secret = db_collection.encrypt_data(
            collection.file_api_secret
        )

    db_collection.save()

    return db_collection


@router.get(
    "/{collection_id}/file_host",
    response_model_by_alias=False,
    response_model=schemas.collections.CollectionFileHostSchema,
)
def get_file_host(
    collection_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_collection = models.Collection.objects(
        id=collection_id, owner=current_user
    ).first()
    if not db_collection:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {collection_id} collection in system",
        )

    data = dict(file_host=db_collection.file_host, file_api_key="", file_api_secret="")

    if db_collection.file_api_key:
        data["file_api_key"] = db_collection.decrypt_data(db_collection.file_api_key)

    if db_collection.file_api_secret:
        data["file_api_secret"] = db_collection.decrypt_data(
            db_collection.file_api_secret
        )

    return data


@router.get(
    "/{collection_id}/download/{archive_name}",
    response_model_by_alias=False,
    response_model=schemas.collections.CollectionFileHostSchema,
)
def download_collection(
    collection_id: str,
    archive_name: str,
    # current_user: models.User = Depends(core.deps.get_current_user),
):
    db_collection = models.Collection.objects(
        id=collection_id,
        # owner=current_user
    ).first()
    if not db_collection:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {collection_id} collection in system",
        )

    archive = pathlib.Path(
        f"{config.settings.HERMES_DATA_DIR}/archive/{db_collection.id}.zip"
    )

    if not archive.exists():
        raise HTTPException(
            status_code=404,
            detail=f"There are no archive file for {db_collection.id} in system",
        )

    data = None
    with open(archive, "rb") as f:
        data = f.read()

    content_type = "application/zip, application/octet-stream, application/x-zip-compressed, multipart/x-zip"
    return Response(content=data, media_type=content_type)
