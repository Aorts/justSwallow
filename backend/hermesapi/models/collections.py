import mongoengine as me
import datetime
import os
import string
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


from . import images

METADATA_FORMATS = [("opensea", "OpenSea")]
FILE_HOSTS = [("pinata", "Pinata")]

COMPONENT_IMAGE_CLASSES = list(string.ascii_uppercase[:10])


class Collection(me.Document):
    meta = {"collection": "collections"}

    name = me.StringField(required=True, max_length=256)
    description = me.StringField()

    external_url_template = me.StringField(default="")
    metadata_format = me.StringField(
        required=True, default="opensea", choices=METADATA_FORMATS
    )
    file_host = me.StringField(required=True, default="pinata", choices=FILE_HOSTS)

    owner = me.ReferenceField("User", dbref=True, required=True)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.utcnow)

    generated_trait = me.IntField(required=True, default=0)

    file_api_key = me.BinaryField(default=b"")
    file_api_secret = me.BinaryField(default=b"")
    file_token_cid = me.StringField()
    file_json_token_cid = me.StringField()
    file_info = me.DictField()

    @property
    def image_amount(self):
        return self.get_art_images().count()

    def to_mongo_all(self):
        data = self.to_mongo()
        data["owner"] = self.owner.to_mongo()
        return data

    def get_art_images(self):
        return images.ArtImage.objects(collection=self)

    def get_key(self):
        password = str(self.id).encode()
        salt = str(self.owner.id).rjust(16, "0")[:16].encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )
        # data = str(self.owner.id).rjust(32, "0")[:32]
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def encrypt_data(self, text):
        key = self.get_key()
        f = Fernet(key)
        return f.encrypt(text.encode())

    def decrypt_data(self, token):

        key = self.get_key()
        f = Fernet(key)
        return f.decrypt(token)


class ComponentImage(me.Document):
    meta = {"collection": "component_images"}
    name = me.StringField(required=True, max_length=256, default="component")
    description = me.StringField()
    image = me.ImageField(collection_name="component_images")

    owner = me.ReferenceField("User", dbref=True, required=True)
    image_layer = me.ReferenceField("ImageLayer", dbref=True, required=True)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.utcnow)

    generated_number = me.IntField(required=True, default=0)

    rarity = me.FloatField(required=True, default=0)
    rarity_percent = me.FloatField(required=True, default=0)
    rarity_weight = me.FloatField(required=True, default=0)

    component_class = me.StringField(
        required=True, default="A", choices=COMPONENT_IMAGE_CLASSES
    )

    @property
    def filename(self):
        if self.image:
            return self.image.filename
        return None

    @property
    def uri(self):
        if self.image:
            return f"/v1/component-images/{self.id}/download/{self.image.filename}"

        return None

    @property
    def url(self):
        uri = self.uri
        if uri:
            base_url = os.getenv("BASE_URL", "http://localhost:8081")
            return f"{base_url}{uri}"

        return None

    def count_art_image(self):
        return images.ArtImage.objects(components=self).count()


class ImageLayer(me.Document):
    meta = {"collection": "image_layers", "strict": False}
    name = me.StringField(required=True, max_length=256, default="layer")
    description = me.StringField()
    order = me.IntField(required=True, default=0)
    required = me.BooleanField(required=True, default=True)

    owner = me.ReferenceField("User", dbref=True, required=True)
    collection = me.ReferenceField("Collection", dbref=True, required=True)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.utcnow)

    def get_images(self, component_class=None):
        if component_class:
            return ComponentImage.objects(
                image_layer=self, component_class=component_class
            )
        return ComponentImage.objects(image_layer=self)


class CollectionOperation(me.Document):
    meta = {"collection": "collection_operations"}

    command_type = me.StringField(required=True, default="generate")
    parameters = me.DictField(default={"generate_typed": "normal-random"})

    collection = me.ReferenceField("Collection", dbref=True, required=True)
    owner = me.ReferenceField("User", dbref=True, required=True)

    amount = me.IntField(required=True, default=0)
    status = me.StringField(required=True, default="wait")

    submitted_date = me.DateTimeField(required=True, default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.utcnow)
    completed_date = me.DateTimeField()

    message = me.DictField()
