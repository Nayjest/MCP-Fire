from mcpfire.http_models import HTTPRequest


def test_request_model():
    model = HTTPRequest(
        url="https://example.com/api",
        method="POST",
        headers={"Content-Type": "application/json"},
        json_payload={"key": "value"},
    )
    assert "key" in model.json_payload
    assert "value" in model.json_payload_str
    model.json_payload_str = model.json_payload_str.replace("value", "new_value")
    assert model.json_payload["key"] == "new_value"
