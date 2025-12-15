import code
import textwrap
import asyncio
from ..http_models import *
from ..http_models.jetbrains import *
from ..bootstrap import bootstrap
from microcore import ui


async def repl():
    """Start an interactive REPL session."""
    await bootstrap()
    banner = textwrap.dedent(
        f"""
        Entering {ui.magenta('MCP-Fire')} REPL.
        Type '{ui.blue('exit()')}' or {ui.yellow('Ctrl-Z')}, {ui.yellow('Return')} to exit.
        """
    ).strip()
    exit_message = "Exiting MCPFire REPL."
    code.interact(banner=banner, exitmsg=exit_message, local=globals())
