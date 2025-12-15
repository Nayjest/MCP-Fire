import yaml
from ..http_models.models import HTTPRequest


# ==========================================
# 2. SAVE MODEL TO YAML FILE
# ==========================================
def save_model_to_yaml(model: HTTPRequest, output_path: str):
    """
    Takes a single HTTPRequest model and saves it as a YAML file.
    """
    # 1. Dump model to dict, excluding None values for cleaner YAML
    data = model.model_dump(exclude_none=True)

    # 2. Convert HttpUrl objects to strings for YAML compatibility
    if 'url' in data:
        data['url'] = str(data['url'])

    # 3. Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
