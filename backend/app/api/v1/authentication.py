from fastapi import APIRouter, HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security import OAuth2PasswordRequestForm

from app import models
from .. import schemas
from .. import core

router = APIRouter(prefix="/authentication", tags=["authentication"])


@router.post(
    "",
)
async def authentication(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = models.User.objects(email=form_data.username).first()

    jwt_handler = core.get_jwt_handler()
    if db_user:
        if db_user.verify_password(form_data.password):
            access_token = jwt_handler.encode_token(db_user)
            refresh_token = jwt_handler.encode_refresh_token(db_user)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }

    raise HTTPException(
        status_code=401,
        detail="Incorrect username or password",
    )


@router.get("/refresh_token")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
):
    refresh_token = credentials.credentials

    jwt_handler = get_jwt_handler()
    new_token = jwt_handler.refresh_token(refresh_token)
    return {"access_token": new_token}


@router.post(
    "/test-token",
    response_model_by_alias=False,
    response_model=schemas.users.UserSchema,
)
async def test_token(current_user: models.User = Depends(core.deps.get_current_user)):
    """
    Test access token
    """
    return current_user
