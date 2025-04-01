from typing import Any

from fastapi import APIRouter, Request
from sqlalchemy.ext.asyncio import AsyncSession

from routers.decorator import allow_unauthorized
from schemas.user_schema import UserBase, UserLogin
from services.user_service import login_user

user_router = APIRouter()


@user_router.post("/users", response_model=UserBase)
@allow_unauthorized
async def login(request: Request, data: UserLogin) -> dict[str, Any]:
    db: AsyncSession = request.state.db
    return await login_user(db, data)
