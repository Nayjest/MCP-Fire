import json
import re
from typing import Any, Dict, List
from urllib.parse import parse_qs, urlparse

from .models import HTTPRequest


# ==========================================
# 1. LOAD MODEL FROM HTTP FILE
# ==========================================
def load_models_from_http_file(file_path: str) -> List[HTTPRequest]:
    """
    Reads a JetBrains .http file, parses all requests contained within,
    and returns a list of Pydantic HTTPRequest models.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by '###' delimiter used in .http files
    raw_blocks = re.split(r'^###.*$', content, flags=re.MULTILINE)

    models = []
    for block in raw_blocks:
        if not block.strip():
            continue

        # Parse the text block into a dictionary
        req_dict = _parse_http_block(block)
        if req_dict:
            # Convert dictionary to Pydantic Model
            models.append(HTTPRequest(**req_dict))

    return models


# ==========================================
# INTERNAL HELPER (Parsing Logic)
# ==========================================
def _parse_http_block(block: str) -> Dict[str, Any]:
    lines = block.strip().splitlines()
    if not lines:
        return {}

    method = "GET"
    url = ""
    headers = {}
    body_lines = []

    is_body = False
    request_line_found = False

    for line in lines:
        stripped = line.strip()

        # Skip comments
        if stripped.startswith('#') or stripped.startswith('//'):
            continue

        # Detect Body start (empty line)
        if request_line_found and stripped == "" and not is_body:
            is_body = True
            continue

        if is_body:
            body_lines.append(line)
            continue

        # Parse Request Line (METHOD URL)
        if not request_line_found:
            # Matches: POST http://google.com OR just http://google.com
            match = re.match(r'^(?:([A-Z]+)\s+)?(.+)$', stripped)
            if match:
                method = match.group(1) if match.group(1) else "GET"
                url = match.group(2)
                request_line_found = True
            continue

        # Parse Headers
        if request_line_found and ':' in stripped:
            key, val = stripped.split(':', 1)
            headers[key.strip()] = val.strip()

    # Extract Query Params from URL
    clean_url, params = _extract_params(url)

    # Process Body
    raw_body = "\n".join(body_lines).strip()
    json_payload = None
    data_payload = None

    if raw_body:
        try:
            json_payload = json.loads(raw_body)
        except json.JSONDecodeError:
            data_payload = raw_body

            # Handle Form Data explicitly if header exists
            if 'application/x-www-form-urlencoded' in headers.get('Content-Type', '').lower():
                # In a real scenario, you might want to parse key=val&key2=val2 here
                pass

    # Construct result dict
    result = {
        "method": method,
        "url": clean_url,
        "headers": headers,
        "params": params,
    }
    if json_payload: result["json_payload"] = json_payload
    if data_payload: result["data_payload"] = data_payload

    return result


def _extract_params(url: str):
    """Separates URL and Query Params."""
    if '{{' in url: return url, {}  # Skip parsing if using variables

    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    # Flatten {'key': ['val']} to {'key': 'val'}
    flat_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

    clean_url = url.split('?')[0]
    return clean_url, flat_params
