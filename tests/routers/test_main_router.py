from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_model import User


async def test_read_hello(client: TestClient, testdb: AsyncSession) -> None:
    response: Response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"Hello": "7 powers"}


async def test_read_hello_with_auth(client: TestClient, testdb: AsyncSession) -> None:
    new_user: User = User(gid="123", gname="gname", picture="picture")
    new_user.access_key = "abc"
    testdb.add(new_user)
    await testdb.commit()

    response: Response = client.get("/hello", headers={"Authorization": "Bearer abc"})
    assert response.status_code == 200

    updated_user: User | None = (await testdb.execute(select(User).filter_by(access_key="abc"))).scalar_one_or_none()
    assert updated_user is not None
    assert updated_user.gid == "123"
    assert updated_user.gname == "gname"
    assert updated_user.picture == "picture"
    assert updated_user.access_key == "abc"
