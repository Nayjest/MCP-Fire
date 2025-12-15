from mcpfire.http_models import HTTPRequest
from mcpfire.http_models.jetbrains import load_models_from_http_file
from ...fixtures import FIXTURES_ROOT


def test_load_jetbrains_http():
    def read(file):
        return load_models_from_http_file(FIXTURES_ROOT / "http" / file)[0]
    model = read("pokemon.http")
    assert isinstance(model, HTTPRequest)
    assert model.method == "POST"
    assert isinstance(model.json_payload, dict)
    assert "query" in model.json_payload
    assert isinstance(model.json_payload_str, str)
    assert "pikachu" in model.json_payload_str
    assert "pikachu" in model.json_payload["query"]
