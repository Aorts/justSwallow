import mongoengine as me
from .users import User
from .collections import Collection, ImageLayer, ComponentImage, CollectionOperation
from .images import ArtImage


def init_mongoengine(settings):

    dbname = settings.MONGODB_DB
    host = settings.MONGODB_HOST
    port = settings.MONGODB_PORT
    username = settings.MONGODB_USERNAME
    password = settings.MONGODB_PASSWORD

    me.connect(db=dbname, host=host, port=port, username=username, password=password)
