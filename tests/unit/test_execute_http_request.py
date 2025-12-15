from mcpfire.http_models import HTTPResponse
from mcpfire.http_models.jetbrains import load_models_from_http_file
from ..fixtures import FIXTURES_ROOT
from mcpfire.core.exec import async_request


async def test_execute_http_request():
    request = load_models_from_http_file(FIXTURES_ROOT / "http" / "pokemon.http")[0]
    response = await async_request(request)
    assert isinstance(response, HTTPResponse)
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")
    assert "Pikachu" in response.text_body
    assert response.json_body["data"]["pokemon"]["classification"] == "Mouse Pokémon"
    assert response.elapsed_seconds > 0
