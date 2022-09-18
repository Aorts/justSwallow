import requests
import json
import datetime
import pathlib
import zipfile
from hermesapi.api.utils import metadata_generators
from hermesapi import models


class FileOperator:
    def __init__(self, collection_operation, data_path="/tmp/hermes"):
        self.collection_operation = collection_operation
        self.data_path = data_path

        self.working_path = pathlib.Path(f"{data_path}/archive")
        if not self.working_path.exists():
            self.working_path.mkdir(parents=True, exist_ok=True)

    def create_temporary(self):

        self.collection_path = self.working_path / str(
            self.collection_operation.collection.id
        )
        if not self.collection_path.exists():
            self.collection_path.mkdir(parents=True, exist_ok=True)

        collection_archive = pathlib.Path(f"{self.collection_path}.zip")
        if collection_archive.exists():
            collection_archive.unlink(missing_ok=True)

    def remove_temporary(self):
        if self.collection_path.exists():
            for file in self.collection_path.iterdir():
                file.unlink(missing_ok=True)

            self.collection_path.rmdir()

    def prepair_art_file(self):
        art_images = models.ArtImage.objects(
            collection=self.collection_operation.collection
        )
        for art_image in art_images:
            with open(f"{self.collection_path}/{art_image.image.filename}", "wb") as f:
                f.write(art_image.image.read())
            with open(
                f"{self.collection_path}/{art_image.image.filename.split('.')[0]}.json",
                "w",
            ) as f:
                f.write(json.dumps(art_image.metadata))

    def create_zip_file(self):
        with zipfile.ZipFile(f"{self.collection_path}.zip", mode="w") as archive:
            for file in self.collection_path.iterdir():
                archive.write(file, arcname=file.name)

    def run(self):

        self.collection_operation.status = "file prepairation"
        self.collection_operation.updated_date = datetime.datetime.utcnow()
        self.collection_operation.save()

        self.create_temporary()

        print("prepair image collection", self.collection_operation.id)
        self.prepair_art_file()

        # self.collection_operation.status = "json prepairation"
        # self.collection_operation.updated_date = datetime.datetime.utcnow()
        # self.collection_operation.save()

        # print("prepair json collection", self.collection_operation.id)
        # self.prepair_json_file()

        self.collection_operation.status = "create archive"
        self.collection_operation.updated_date = datetime.datetime.utcnow()
        self.collection_operation.save()

        print("create zip file", self.collection_operation.id)
        self.create_zip_file()

        self.remove_temporary()

        self.collection_operation.status = "completed"
        self.collection_operation.updated_date = datetime.datetime.utcnow()
        self.collection_operation.completed_date = datetime.datetime.utcnow()
        self.collection_operation.save()


def create_archive(collection_operation, data_path):
    operator = FileOperator(collection_operation, data_path)
    operator.run()
