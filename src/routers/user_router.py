from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from setup.setting import get_db
from models.user_model import User
from schemas.user_schema import UserCreate
from services.user_service import create_user_entity

user_router = APIRouter()


@user_router.get("/users")
async def list_users():
    users = Depends(get_db).query(User).all()
    return {"data": users}


@user_router.post("/users")
async def create_user(data: dict, db: Session = Depends(get_db)):
    user = UserCreate(**data)
    return create_user_entity(db=db, user=user)


@user_router.put("/users/{user_id}")
async def update_user():
    pass


@user_router.delete("/users/{user_id}")
async def delete_user():
    pass
