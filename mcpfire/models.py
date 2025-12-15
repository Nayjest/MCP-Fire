from typing import Any

from pydantic import BaseModel, model_validator


class ToolArgument(BaseModel):
    name: str
    type: str = "string"
    description: str = ""
    required: bool
    default: Any = None
    placeholder: str = ""

    @model_validator(mode='before')
    @classmethod
    def _set_required(cls, data):
        if isinstance(data, dict) and 'required' not in data:
            data['required'] = 'default' not in data
        return data


class ToolMapping(BaseModel):
    name: str
    title: str = ""
    description: str = ""
    request_file: str
    args: list[ToolArgument]

    @property
    def args_dict(self) -> dict[str, ToolArgument]:
        return {arg.name: arg for arg in self.args}


class MCPServerDefinition(BaseModel):
    name: str
    tools: list[ToolMapping]
    path: str

    @model_validator(mode='before')
    @classmethod
    def _init_path(cls, data):
        if isinstance(data, dict):
            if 'path' not in data or not data['path']:
                data['path'] = "/" + data.get('name', '')
            else:
                if not data['path'].startswith('/'):
                    data['path'] = '/' + data['path']
        return data
