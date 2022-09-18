import copy


class SimpleMetadataGenerator:
    def __init__(self):
        self.template = dict(
            name="",
            description="",
            image="ipfs://{token_cid}/{filename}",
            attributes=[],
        )


class OpenseaMetadataGenerator(SimpleMetadataGenerator):
    def __init__(self):
        super().__init__()

    def compose(self, art_image):
        collection = art_image.collection
        data = copy.deepcopy(self.template)
        data["name"] = art_image.name
        data["description"] = art_image.description
        data["image"] = data["image"].format(
            token_cid=collection.file_token_cid, filename=art_image.image.filename
        )
        data["external_url"] = collection.external_url_template.format(
            id=str(art_image.id),
            filename=art_image.image.filename,
            filename_without_extension=art_image.image.filename.split(".")[0],
        )

        data["attributes"] = []
        for component in art_image.components:
            data["attributes"].append(
                dict(trait_type=component.image_layer.name, value=component.name)
            )

        return data
