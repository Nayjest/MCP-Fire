import logging
from typing import Any

import config_reading
from fastmcp import FastMCP
from fastmcp.tools import Tool, FunctionTool
from fastmcp.server.http import StarletteWithLifespan
from fastmcp.tools.tool import ToolResult
from pydantic import PrivateAttr
from rich.pretty import pprint

from .http_models import HTTPRequest
from .models import MCPServerDefinition, ToolMapping


class ExecutableHttpRequestTool(Tool):
    mapping: ToolMapping
    _request_model: HTTPRequest = PrivateAttr()

    def model_post_init(self, __context):
        self._request_model = HTTPRequest.load(self.mapping.request_file)

    @staticmethod
    def from_mapping(tool: ToolMapping) -> "ExecutableHttpRequestTool":
        parameters = {
            "properties": (props := {}),
            "required": (required := []),
            "type": "object",
        }
        for arg in tool.args:
            props[arg.name] = (prop := {
                "type": arg.type,
                "title": arg.name,
            })
            if arg.description:
                prop["description"] = arg.description
            if arg.required:
                required.append(arg.name)
            else:
                prop["default"] = arg.default

        fastmcp_tool = ExecutableHttpRequestTool(
            name=tool.name,
            description=tool.description,
            mapping=tool,
            parameters=parameters
        )
        return fastmcp_tool

    async def run(self, arguments: dict[str, Any]) -> ToolResult:
        pprint(arguments)
        variables = {
            self.mapping.args_dict[arg_name].placeholder: arg_value
            for arg_name, arg_value in arguments.items()
        }
        request = self._request_model.substitute_variables(variables) if variables else self._request_model
        response = await request.execute()
        if response.json_body is not None:
            return ToolResult(structured_content=response.json_body)
        return ToolResult([response.text_body])


def to_fastmcp_tool(tool: ToolMapping) -> Tool:
    return ExecutableHttpRequestTool.from_mapping(tool)


class MCPSubServer:
    mcp_app: StarletteWithLifespan
    definition: MCPServerDefinition

    def __init__(self, definition: MCPServerDefinition):
        self.definition = definition
        mcp = FastMCP(name=definition.name)
        for tool in definition.tools:
            mcp.add_tool(t:=to_fastmcp_tool(tool))
            logging.info(f"Tool '{t.name}' added to MCP server '{definition.name}'")
        self.mcp_app = mcp.http_app(path="/mcp")


def create_mcp_servers() -> list[MCPSubServer]:
    from .service_container import svc
    from .models import MCPServerDefinition
    sub_servers = []
    for item in svc.config.mcp_servers:
        if isinstance(item, str):
            logging.info("Loading MCP server config from file: %s...", item)
            cfg = config_reading.read_config(item)
            df = MCPServerDefinition(**cfg)
            sub_server = MCPSubServer(df)
            sub_servers.append(sub_server)
    return sub_servers
