import yaml

from mcpfire.http_models import HTTPRequest


def load_request_from_yaml(file_path: str) -> HTTPRequest:
    with open(file_path, 'r') as f:
        raw_data = yaml.safe_load(f)
    return HTTPRequest(**raw_data)
