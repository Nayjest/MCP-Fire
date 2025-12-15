"""Fixtures package for tests."""
from pathlib import Path

from mcpfire.http_models import HTTPRequest

FIXTURES_ROOT = Path(__file__).resolve().parent


class Requests:
    @staticmethod
    def pokemon() -> HTTPRequest:
        return HTTPRequest.load(FIXTURES_ROOT / "http" / "pokemon.http")
