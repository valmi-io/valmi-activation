from fastapi import APIRouter

from api.logic.user_service import UserService
from api.models.user import User

router = APIRouter(prefix="/users")
user_service = UserService()


@router.post("/")
async def greet(user: User) -> str:
    return user_service.greet(user)
