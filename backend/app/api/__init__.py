import os

from fastapi import FastAPI

from .. import models
from .. import config
from .routes import register_routers
from . import redis_rq


from fastapi.middleware.cors import CORSMiddleware


origins = ["http://localhost:3000", "localhost:3000"]


def create_app():
    environment = os.getenv("SWALLOW_ENV") or "development"
    settings = config.get_config(environment)

    app = FastAPI(title="Swallow API")

    register_routers(app)

    @app.get("/")
    def index():
        return settings.CONFIG_NAME

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    models.init_mongoengine(settings)
    redis_rq.init_rq(settings)
    return app
