from fastapi import APIRouter


router = APIRouter(prefix="/v1")


@router.get("/", status_code=200)
def root() -> dict:
    """
    V1
    """
    return {"msg": "Hello, HERMES API V1"}
