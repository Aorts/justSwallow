from fastapi import APIRouter, HTTPException, Depends

from hermesapi import models
from .. import schemas
from .. import core

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model_by_alias=False, response_model=schemas.users.UserSchema)
def create(user: schemas.users.UserRegistrationSchema):
    """
    Create User
    """
    db_user = models.User.objects(email=user.email).first()

    if db_user:
        raise HTTPException(  # 5
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    db_user = models.User(**user.dict())
    db_user.set_password(user.password)
    db_user.save()

    return schemas.users.UserSchema.parse_obj(db_user.to_mongo())


@router.get(
    "/me", response_model_by_alias=False, response_model=schemas.users.UserSchema
)
def get_me(current_user: models.User = Depends(core.deps.get_current_user)):

    return current_user


@router.put(
    "/me", response_model_by_alias=False, response_model=schemas.users.UserSchema
)
def update_me(
    user: schemas.users.UserUpdatedSchema,
    current_user: models.User = Depends(core.deps.get_current_user),
):
    set_dict = {f"set__{k}": v for k, v in user.dict().items() if v is not None}
    current_user.update(**set_dict)
    current_user.reload()

    return current_user
