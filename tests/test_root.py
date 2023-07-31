import pytest
pytestmark = pytest.mark.order(1)

@pytest.mark.asyncio
async def test_root(client):
   response = await client.get('/')
   assert response.status_code == 200
   assert response.json() == {"message": "Hello World!"}