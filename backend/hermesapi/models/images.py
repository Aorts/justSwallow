import mongoengine as me
import datetime
import os
from hermesapi.api.utils import metadata_generators


class ArtImage(me.Document):
    meta = {"collection": "art_images"}

    name = me.StringField(required=True, max_length=256, default="ArtImage")
    description = me.StringField(default="")

    rarity = me.FloatField(required=True, default=0)
    rarity_percent = me.FloatField(required=True, default=0)

    image_class = me.StringField(required=True, default="A")
    image = me.ImageField(collection_name="art_images")

    owner = me.ReferenceField("User", dbref=True, required=True)
    collection = me.ReferenceField("Collection", dbref=True, required=True)
    components = me.ListField(
        me.ReferenceField("ComponentImage", dbref=True, required=True)
    )
    command = me.ReferenceField("CollectionOperation", dbref=True, required=True)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.utcnow)

    @property
    def filename(self):
        if self.image:
            return self.image.filename

        return None

    @property
    def uri(self):
        if self.image:
            return f"/v1/art-images/{self.id}/download/{self.image.filename}"

        return None

    @property
    def url(self):
        base_url = os.getenv("BASE_URL", "http://localhost:8081")
        if self.uri:
            return f"{base_url}{self.uri}"
        return None

    @property
    def metadata(self):
        generator = metadata_generators.OpenseaMetadataGenerator()

        return generator.compose(self)

    @property
    def trait_rarity(self):
        data = dict(
            rarity=self.rarity, total=self.collection.generated_trait, attributes=dict()
        )
        for component in self.components:
            data["attributes"][component.name] = dict(
                count=component.generated_number,
                rarity=component.rarity,
                rarity_percent=component.rarity_percent,
            )
        return data
