from .server import WorkerServer
from ..config import get_config
import os


def create_server():
    environment = os.getenv("SWALLOW_ENV") or "development"
    settings = get_config(environment)
    server = WorkerServer(settings)

    return server
