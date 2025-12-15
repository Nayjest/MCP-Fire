import logging

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from fastmcp.server.http import StarletteWithLifespan
from .mcp_builder import create_mcp_servers
from .service_container import svc


@asynccontextmanager
async def root_lifespan(app: FastAPI):
    yield


def combine_lifespans(mcp_app: StarletteWithLifespan, outer: callable) -> callable:
    @asynccontextmanager
    async def combined_lifespan(app: FastAPI):
        async with outer(app):
            async with mcp_app.lifespan(app):
                yield

    return combined_lifespan


async def create_web_app() -> FastAPI:
    sub_servers = create_mcp_servers()
    lifespan = root_lifespan
    for sub_server in sub_servers:
        lifespan = combine_lifespans(sub_server.mcp_app, lifespan)
    app = FastAPI(lifespan=lifespan)
    add_request_logging_middleware(app)
    for sub_server in sub_servers:
        app.mount(
            svc.config.mcp_servers_url_prefix + sub_server.definition.path,
            sub_server.mcp_app
        )
    return app


def add_request_logging_middleware(app: FastAPI):
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        response = await call_next(request)
        logging.info(f"{request.method} {request.url} --> {response.status_code}")
        return response
