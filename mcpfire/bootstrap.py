import sys
import logging
from .service_container import svc
from .config import Config
from config_reading import read_config
from rich.pretty import install

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

async def bootstrap(config: str = "config.yml"):
    setup_logging()
    install()
    logging.info("Bootstrapping... %s", config)
    config_data = read_config(config)
    svc.config = Config(**config_data)