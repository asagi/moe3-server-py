from typing import override

from fastapi import Depends, FastAPI, Request, Response
from fastapi.concurrency import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.database import AsyncSessionLocal, get_db
from routers import all_routers
from setup.load_models import Power, load_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        await load_cache(session)
    yield


app = FastAPI(lifespan=lifespan)


class BackgroundMiddleware(BaseHTTPMiddleware):
    @override
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        await self.background_task()
        response: Response = await call_next(request)
        return response

    async def background_task(self) -> None:
        # TODO: バックグラウンドタスクの実装
        print("Background task running")


app.add_middleware(BackgroundMiddleware)


@app.get("/hello")
async def hello_world(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    powers = (await db.execute(select(Power))).all()
    return {"Hello": f"{len(powers)} powers"}


for router in all_routers:
    app.include_router(router)
