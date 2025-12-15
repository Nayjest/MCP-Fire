import json
from os import PathLike
from typing import Any, Dict, Literal, Optional, Union

import config_reading
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


# ===========================
# 1. REQUEST MODEL (INPUT)
# ===========================
class HTTPRequest(BaseModel):
    url: Union[HttpUrl, str]
    method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'] = 'GET'

    headers: Dict[str, str] = Field(default_factory=dict)
    cookies: Dict[str, str] = Field(default_factory=dict)
    params: Dict[str, Any] = Field(default_factory=dict)

    # Tuple for Basic Auth (username, password)
    auth: Optional[tuple[str, str]] = None

    # Payloads
    json_payload: Optional[Any] = None
    data_payload: Optional[Union[Dict[str, Any], str, bytes]] = None

    # Config
    timeout: float = 30.0
    follow_redirects: bool = True  # Renamed from requests' 'allow_redirects' to match httpx
    description: Optional[str] = Field(
        default=None,
        description="Optional description of the HTTP request."
    )

    @model_validator(mode='after')
    def check_payload_exclusivity(self):
        if self.json_payload is not None and self.data_payload is not None:
            raise ValueError("Cannot define both 'json_payload' and 'data_payload'.")
        return self

    @property
    def json_payload_str(self) -> Optional[str]:
        if self.json_payload is None:
            return None
        return json.dumps(self.json_payload)

    @json_payload_str.setter
    def json_payload_str(self, value: Optional[str]):
        if value is None:
            self.json_payload = None
        else:
            self.json_payload = json.loads(value)

    @staticmethod
    def load(file: str | PathLike) -> "HTTPRequest":
        from .jetbrains import load_models_from_http_file
        if str(file).endswith('.http'):
            models = load_models_from_http_file(file)
            return models[0]
        else:
            config = config_reading.read_config(file)
            return HTTPRequest(**config)

    async def execute(self) -> "HTTPResponse":
        from ..core.exec import async_request
        return await async_request(self)

    def to_jetbrains_http(self) -> str:
        from .jetbrains import to_jetbrains_http
        return to_jetbrains_http(self)

    def substitute_variables(self, variables: Dict[str, str]) -> "HTTPRequest":
        data = json.dumps(self.model_dump())
        for key, value in variables.items():
            if key not in data:
                raise ValueError("Variable key not found in request data.")
            data = data.replace(key, value)
        return HTTPRequest(**json.loads(data))


# ===========================
# 2. RESPONSE MODEL (OUTPUT)
# ===========================
class HTTPResponse(BaseModel):
    # Allow arbitrary types because 'headers' might be complex,
    # though we usually convert them to dict.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    status_code: int
    url: HttpUrl
    method: str

    # Response Metadata
    headers: Dict[str, str]
    cookies: Dict[str, str]
    elapsed_seconds: float

    # Response Body
    text_body: str
    # If the response is valid JSON, this will contain the object, otherwise None
    json_body: Optional[Any] = None

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300
