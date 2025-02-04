from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from schemas.user_schema import UserBase, UserLogin
from services.user_service import login_user

user_router = APIRouter()


@user_router.post("/users", response_model=UserBase)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    return await login_user(db, data)
