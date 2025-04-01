from fastapi.testclient import TestClient
from httpx import Response


async def test_read_hello(client: TestClient) -> None:
    response: Response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"Hello": "7 powers"}
