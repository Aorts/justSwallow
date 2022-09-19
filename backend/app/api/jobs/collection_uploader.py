import requests
import json
import datetime
from app.api.utils import metadata_generators


class PinataUploader:
    def __init__(self, collection_operation):
        self.collection_operation = collection_operation

        self.pin_file_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    def get_files(self):
        files = []
        collection = self.collection_operation.collection
        for art_image in collection.get_art_images():
            image = art_image.image
            files.append(
                (
                    "file",
                    (
                        f"{collection.name}/{image.filename}",
                        image.read(),
                        image.content_type,
                    ),
                )
            )
        return files

    def get_metadata(self):
        metadata_gernerator = metadata_generators.OpenseaMetadataGenerator()
        files = []

        collection = self.collection_operation.collection
        for art_image in collection.get_art_images():
            filename = art_image.image.filename.split(".")[0]

            metadata = metadata_gernerator.compose(art_image)
            files.append(
                (
                    "file",
                    (
                        f"{collection.name}-json/{filename}",
                        json.dumps(metadata).encode(),
                        "application/json",
                    ),
                )
            )
        return files

    def get_auth_header(self):
        collection = self.collection_operation.collection
        if not (collection.file_api_key and collection.file_api_secret):
            raise Exception("api key or api secret not found")

        api_key = collection.decrypt_data(collection.file_api_key)
        api_secret = collection.decrypt_data(collection.file_api_secret)

        headers = {
            "pinata_api_key": api_key,
            "pinata_secret_api_key": api_secret,
        }

        return headers

    def upload(self):

        headers = self.get_auth_header()

        files = self.get_files()

        response: requests.Response = requests.post(
            url=self.pin_file_url, files=files, headers=headers
        )

        data = response.json()

        self.collection_operation.amount = len(files)
        self.collection_operation.save()

        collection = self.collection_operation.collection
        collection.file_token_cid = data.get("IpfsHash", "")
        collection.file_info["token_cid"] = data
        collection.save()

        print("upload complete cid:", collection.file_token_cid)

    def upload_metadata(self):
        headers = self.get_auth_header()

        files = self.get_metadata()

        response: requests.Response = requests.post(
            url=self.pin_file_url, files=files, headers=headers
        )

        data = response.json()

        collection = self.collection_operation.collection
        collection.file_json_token_cid = data.get("IpfsHash", "")
        collection.file_info["json_token_cid"] = data
        collection.save()

        print("upload metadata complete cid:", collection.file_json_token_cid)

    def run(self):

        self.collection_operation.status = "image uploading"
        self.collection_operation.updated_date = datetime.datetime.utcnow()
        self.collection_operation.save()

        print("upload image collection", self.collection_operation.id)
        self.upload()

        self.collection_operation.status = "metadata uploading"
        self.collection_operation.updated_date = datetime.datetime.utcnow()
        self.collection_operation.save()

        print("upload json collection", self.collection_operation.id)
        self.upload_metadata()

        self.collection_operation.status = "completed"
        self.collection_operation.updated_date = datetime.datetime.utcnow()
        self.collection_operation.completed_date = datetime.datetime.utcnow()
        self.collection_operation.save()


def upload(collection_operation):
    uploader = None
    if collection_operation.collection.file_host == "pinata":
        uploader = PinataUploader(collection_operation)

    if uploader:
        uploader.run()
