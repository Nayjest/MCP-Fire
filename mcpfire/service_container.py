from dataclasses import dataclass

from .config import Config


@dataclass
class ServiceContainer:
    config: Config = None


svc = ServiceContainer()
