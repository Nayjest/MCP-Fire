from os import PathLike
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Main configuration model matching config.toml structure."""
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    ssl_keyfile: str | None = None
    """ Path to SSL key file for HTTPS support, if None, HTTP is used. """
    ssl_certfile: str | None = None
    """ Path to SSL certificate file for HTTPS support, if None, HTTP is used. """
    mcp_servers_url_prefix: str = "/servers"
    """ Prefix for all MCP endpoints"""
    dev_autoreload: bool = False
    mcp_servers: list[dict | str | PathLike] = None
