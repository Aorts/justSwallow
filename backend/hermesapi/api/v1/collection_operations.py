from fastapi import APIRouter, HTTPException, Depends

import datetime


from hermesapi import models, config
from hermesapi.api import redis_rq
from hermesapi.api.jobs import art_generator
from hermesapi.api.jobs import collection_uploader
from hermesapi.api.jobs import file_operator
from .. import schemas
from .. import core

router = APIRouter(prefix="/collection-operations", tags=["collection-operations"])


@router.post(
    "/{collection_id}/generate",
    response_model_by_alias=False,
    response_model=schemas.collection_operations.CollectionOperationSchema,
)
def generate(
    collection_id: str,
    collection_operation: schemas.collection_operations.CollectionOperationGeneratorSchema,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_collection = models.Collection.objects(
        id=collection_id, owner=current_user
    ).first()
    if not db_collection:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {collection_operation.collection_id} collection in system",
        )

    now = datetime.datetime.utcnow()
    db_collection_operation = models.CollectionOperation(
        owner=current_user,
        collection=db_collection,
        amount=collection_operation.amount,
        submitted_date=now,
        parameters=dict(
            generated_type=collection_operation.generated_type,
            generated_class=collection_operation.generated_class,
        ),
    )
    db_collection_operation.save()

    kwargs = {}

    try:
        job = redis_rq.redis_queue.queue.enqueue(
            art_generator.generate,
            args=(db_collection_operation,),
            kwargs=kwargs,
            job_id=f"collection_operation_{db_collection_operation.id}",
            timeout=600,
            job_timeout=21600,
        )
    except Exception as e:
        db_collection_operation.satus = "error"
        db_collection_operation.updated_date = datetime.datetime.now()
        db_collection_operation.save()
        raise HTTPException(
            status_code=500,
            detail=f"Connot complete job, {e}",
        )

    db_collection_operation.status = job.get_status()
    db_collection_operation.updated_date = datetime.datetime.now()
    db_collection_operation.save()

    return db_collection_operation


@router.post(
    "/{collection_id}/count-trait",
    response_model_by_alias=False,
    response_model=schemas.collection_operations.CollectionOperationSchema,
)
def count_trait(
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

    now = datetime.datetime.utcnow()
    db_collection_operation = models.CollectionOperation(
        command_type="count-trait",
        owner=current_user,
        collection=db_collection,
        submitted_date=now,
    )
    db_collection_operation.save()

    kwargs = {}

    try:
        job = redis_rq.redis_queue.queue.enqueue(
            art_generator.count_trait,
            args=(db_collection_operation,),
            kwargs=kwargs,
            job_id=f"collection_operation_{db_collection_operation.id}",
            timeout=600,
            job_timeout=1200,
        )
    except Exception as e:
        db_collection_operation.satus = "error"
        db_collection_operation.updated_date = datetime.datetime.now()
        db_collection_operation.save()
        raise HTTPException(
            status_code=500,
            detail=f"Connot complete job, {e}",
        )

    db_collection_operation.status = job.get_status()
    db_collection_operation.updated_date = datetime.datetime.now()
    db_collection_operation.save()

    return db_collection_operation


@router.post(
    "/{collection_id}/shake-token-id",
    response_model_by_alias=False,
    response_model=schemas.collection_operations.CollectionOperationSchema,
)
def shake_token_id(
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

    now = datetime.datetime.utcnow()
    db_collection_operation = models.CollectionOperation(
        command_type="count-trait",
        owner=current_user,
        collection=db_collection,
        submitted_date=now,
    )
    db_collection_operation.save()

    kwargs = {}

    try:
        job = redis_rq.redis_queue.queue.enqueue(
            art_generator.shake_token_id,
            args=(db_collection_operation,),
            kwargs=kwargs,
            job_id=f"collection_operation_{db_collection_operation.id}",
            timeout=600,
            job_timeout=1200,
        )
    except Exception as e:
        db_collection_operation.satus = "error"
        db_collection_operation.updated_date = datetime.datetime.now()
        db_collection_operation.save()
        raise HTTPException(
            status_code=500,
            detail=f"Connot complete job, {e}",
        )

    db_collection_operation.status = job.get_status()
    db_collection_operation.updated_date = datetime.datetime.now()
    db_collection_operation.save()

    return db_collection_operation


@router.post(
    "/{collection_id}/upload",
    response_model_by_alias=False,
    response_model=schemas.collection_operations.CollectionOperationSchema,
)
def upload(
    collection_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_collection = models.Collection.objects(
        id=collection_id, owner=current_user
    ).first()
    if not db_collection:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {collection_operation.collection_id} collection in system",
        )

    now = datetime.datetime.utcnow()
    db_collection_operation = models.CollectionOperation(
        command_type="upload",
        owner=current_user,
        collection=db_collection,
        submitted_date=now,
    )
    db_collection_operation.save()

    kwargs = {}

    try:
        job = redis_rq.redis_queue.queue.enqueue(
            collection_uploader.upload,
            args=(db_collection_operation,),
            kwargs=kwargs,
            job_id=f"collection_operation_{db_collection_operation.id}",
            timeout=600,
            job_timeout=1200,
        )
    except Exception as e:
        db_collection_operation.satus = "error"
        db_collection_operation.updated_date = datetime.datetime.now()
        db_collection_operation.save()
        raise HTTPException(
            status_code=500,
            detail=f"Connot complete job, {e}",
        )

    db_collection_operation.status = job.get_status()
    db_collection_operation.updated_date = datetime.datetime.now()
    db_collection_operation.save()

    return db_collection_operation


@router.post(
    "/{collection_id}/create-archive",
    response_model_by_alias=False,
    response_model=schemas.collection_operations.CollectionOperationSchema,
)
def create_archive(
    collection_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    db_collection = models.Collection.objects(
        id=collection_id, owner=current_user
    ).first()
    if not db_collection:
        raise HTTPException(
            status_code=404,
            detail=f"There are no {collection_operation.collection_id} collection in system",
        )

    now = datetime.datetime.utcnow()
    db_collection_operation = models.CollectionOperation(
        command_type="create-archive",
        owner=current_user,
        collection=db_collection,
        submitted_date=now,
    )
    db_collection_operation.save()

    kwargs = {}

    try:
        job = redis_rq.redis_queue.queue.enqueue(
            file_operator.create_archive,
            args=(db_collection_operation, config.settings.HERMES_DATA_DIR),
            kwargs=kwargs,
            job_id=f"collection_operation_{db_collection_operation.id}",
            timeout=600,
            job_timeout=1200,
        )
    except Exception as e:
        db_collection_operation.satus = "error"
        db_collection_operation.updated_date = datetime.datetime.now()
        db_collection_operation.save()
        raise HTTPException(
            status_code=500,
            detail=f"Connot complete job, {e}",
        )

    db_collection_operation.status = job.get_status()
    db_collection_operation.updated_date = datetime.datetime.now()
    db_collection_operation.save()

    return db_collection_operation


@router.get(
    "/{collection_operation_id}",
    response_model_by_alias=False,
    response_model=schemas.collection_operations.CollectionOperationSchema,
)
def get_job_status(
    collection_operation_id: str,
    current_user: models.User = Depends(core.deps.get_current_user),
):

    db_collection_operation = models.CollectionOperation.objects(
        id=collection_operation_id
    ).first()

    if not db_collection_operation:
        raise HTTPException(
            status_code=404,
            detail=f"There are no collection_operation {collection_operation_id} in current generator",
        )

    return db_collection_operation
