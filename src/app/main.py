from typing import override

from fastapi import FastAPI, Request, Response
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.database import AsyncSessionLocal, get_db
from routers import all_routers
from routers.decorator import allow_unauthorized, unauthorized_endpoints
from setup.load_models import Power, load_cache

security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        await load_cache(session)
    yield


class AuthorizationMiddleware(BaseHTTPMiddleware):
    @override
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        db: AsyncSession = await get_db().__anext__()
        request.state.db = db

        try:
            credentials: HTTPAuthorizationCredentials | None = await security(request)
            if not credentials and request.url.path not in app.state.allow_unauthorized_routes:
                return JSONResponse(status_code=401, content={"detail": "Authorization header missing"})

            if credentials:
                token = credentials.credentials  # Bearer トークン部分を取得
                # TODO: トークンを元にユーザーを特定して最終アクセス時刻を更新する
                _ = token
                ...

            return await call_next(request)

        finally:
            await db.close()


class BackgroundMiddleware(BaseHTTPMiddleware):
    @override
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        await self.background_task(request.state.db)
        return await call_next(request)

    async def background_task(self, db: AsyncSession) -> None:
        # TODO: バックグラウンドタスクの実装
        ...


app = FastAPI(lifespan=lifespan)
app.add_middleware(BackgroundMiddleware)
app.add_middleware(AuthorizationMiddleware)


for router in all_routers:
    app.include_router(router)


@app.get("/hello")
@allow_unauthorized
async def hello_world(request: Request) -> dict[str, str]:
    db: AsyncSession = request.state.db
    powers = (await db.execute(select(Power))).all()
    return {"Hello": f"{len(powers)} powers"}


allow_unauthorized_routes: set[str] = set()
for route in app.routes:
    if isinstance(route, APIRoute) and hasattr(route, "endpoint"):
        if route.endpoint.__name__ in unauthorized_endpoints:
            allow_unauthorized_routes.add(route.path)

app.state.allow_unauthorized_routes = allow_unauthorized_routes
