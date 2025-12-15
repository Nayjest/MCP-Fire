from typing import Optional

from cyclopts import App
import hypercorn.asyncio
import hypercorn.config

from .server import create_web_app
from .bootstrap import bootstrap
from .service_container import svc

cli = App()
from mcpfire.cli_commands.repl import repl
#cli.command("mcpfire.cli_commands.repl:repl")
cli.command(repl)

@cli.default()
async def run_server(
    config: str = "config.yml",
    debug: bool = False,
    env_file: Optional[str] = None
):
    """
    Default command for CLI application: Run LM-Proxy web server
    """
    await bootstrap(config=config)
    config = hypercorn.config.Config()
    config.bind = [f"{svc.config.host}:{svc.config.port}", "0.0.0.0:8000"]
    config.keyfile = svc.config.ssl_keyfile
    config.certfile = svc.config.ssl_certfile
    app = await create_web_app()

    await hypercorn.asyncio.serve(app, config)