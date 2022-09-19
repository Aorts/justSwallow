from app import models

import pathlib
from PIL import Image
import random
import hashlib
import io
import datetime
import itertools
import collections


class SimpleImageGenerator:
    def __init__(self, collection_operation):
        self.collection_operation = collection_operation
        self.MAX_TRY = 1000

    def create_image(self, image_id, components):
        components[0].image.seek(0)
        data = components[0].image.read()
        img = Image.open(io.BytesIO(data))
        image_class = components[0].component_class
        for component in components[1:]:
            component.image.seek(0)
            data = component.image.read()
            new_layer_img = Image.open(io.BytesIO(data))
            img.paste(new_layer_img, (0, 0), new_layer_img)

        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")

        name = f"{image_id}"

        art_image = models.ArtImage(
            name=f"#{name}",
            description=f"#{name}",
            collection=self.collection_operation.collection,
            owner=self.collection_operation.owner,
            command=self.collection_operation,
            components=components,
            image_class=image_class,
        )
        art_image.image.put(img_bytes, filename=f"{name}.png", content_type="image/png")
        art_image.save()

    def get_posible_image(self, layers):
        posible_image = 1
        if len(layers) == 0:
            return posible_image

        for l, components in layers.items():
            counter = 0
            for k, component in components.items():
                if component["quota"] > 0:
                    counter += 1

            if counter > 0:
                counter += 1
            else:
                continue

            posible_image *= counter

        return posible_image

    def random_component_images(self, layers):
        results = []

        for layer in layers:
            component_image = random.choice(layer)
            if not component_image:
                continue

            results.append(component_image)

        return results

    def is_valide_dna(self, components):
        art_image = models.ArtImage.objects(
            collection=self.collection_operation.collection, components=components
        ).first()

        if art_image:
            return False

        for c in components:
            print("->", c.image_layer.name, ":", c.name, end=" ")
        print()

        return True

    def count_trait(self):

        statistic = {}

        collection = self.collection_operation.collection

        art_images = models.ArtImage.objects(collection=collection)
        for ai in art_images:
            for c in ai.components:
                if c not in statistic:
                    statistic[c] = 0
                statistic[c] += 1

        total = sum(statistic.values())

        total_image = len(art_images)
        for component, v in statistic.items():
            component.generated_number = v
            component.rarity = 1 / (v / total)
            component.rarity_percent = v / total_image * 100
            component.save()

        collection.generated_trait = total
        collection.save()

        art_images = models.ArtImage.objects(collection=collection).order_by("name")
        counter = 1
        for ai in art_images:
            rarity = 0
            rarity_percent = 0
            for component in ai.components:
                rarity += component.rarity
                rarity_percent += component.rarity_percent

            ai.rarity_percent = rarity_percent / len(ai.components)
            ai.rarity = rarity
            ai.name = f"{ai.filename}"
            ai.description = f"#{ai.filename}"
            counter += 1
            print(ai.name, ai.image.filename)
            ai.save()

    def shake_token_id(self):
        art_images = list(
            models.ArtImage.objects(collection=self.collection_operation.collection)
        )
        art_images = random.sample(art_images, len(art_images))
        for index, ai in enumerate(art_images):
            ai.name = f"#{index+1}"
            ai.description = f"#{index+1}"
            buffer_image = io.BytesIO(ai.image.read())
            ai.image.replace(
                buffer_image,
                filename=f"{index+1}.png",
                content_type=ai.image.content_type,
            )
            ai.save()
            print(ai.name, ai.image.filename)

    def get_component_quotas(self, component_class="A"):
        image_layers = models.ImageLayer.objects(
            collection=self.collection_operation.collection,
        ).order_by("order")

        amount = self.collection_operation.amount

        layers = collections.OrderedDict()
        for il in image_layers:
            image_components = dict()
            total = 0
            for image_component in list(il.get_images(component_class=component_class)):
                quota = int(round(amount * (image_component.rarity_weight / 100)))
                if quota == 0:
                    continue

                data = dict(
                    quota=0,
                    count=image_component.count_art_image(),
                    component=image_component,
                )
                if quota + total < amount:
                    data["quota"] = quota
                    total += quota
                else:
                    data["quota"] = amount - total
                    total = total + data["quota"]

                if data["count"] >= data["quota"]:
                    continue

                image_components[image_component.id] = data

            if len(image_components) > 0:
                layers[il] = image_components

            if not il.required:
                allowed_none = 20
                quota = amount - total
                if quota <= 0:
                    quota = int(round((allowed_none / 100) * amount))

                data = dict(quota=quota, count=0, component=None)
                image_components[None] = data

        return layers

    def generate(self, counter, until, layers):
        component_layers = []
        for l in layers.values():
            component_layers.append(list(l.values()))

        while counter < until:
            components = None
            ccomponents = []
            for i in range(self.MAX_TRY):
                ccomponents = self.random_component_images(component_layers)
                prepair_components = [
                    c["component"] for c in ccomponents if c["component"]
                ]

                if self.is_valide_dna(prepair_components):
                    components = prepair_components
                    break

            counter += 1
            if not components:
                continue

            print(f"normal-random -> create image {counter}")
            self.create_image(counter, components)

            for c in ccomponents:
                c["count"] += 1
                if c["count"] < c["quota"]:
                    continue

                for i, l in enumerate(component_layers):
                    if c in l:
                        l.remove(c)

            component_layers[:] = [l for l in component_layers if l]


    def run(self):
        print(
            "Action",
            self.collection_operation.submitted_date,
            self.collection_operation.collection.name,
            self.collection_operation.owner.first_name,
        )
        self.collection_operation.status = "prepair"
        self.collection_operation.updated_date = datetime.datetime.utcnow()
        self.collection_operation.save()

        component_class = self.collection_operation.parameters.get("generated_class")
        layers = self.get_component_quotas(component_class)

        possible_image = self.get_posible_image(layers)

        counter = models.ArtImage.objects(
            collection=self.collection_operation.collection
        ).count()

        amount = self.collection_operation.amount
        if amount > possible_image:
            amount = possible_image

        until = counter + amount

        print("=> start", counter, "to", until, "amount", amount)

        self.collection_operation.status = "generate"
        self.collection_operation.updated_date = datetime.datetime.utcnow()
        self.collection_operation.save()

        self.generate(counter, until, layers)

        self.collection_operation.status = "trait-counting"
        self.collection_operation.updated_date = datetime.datetime.utcnow()
        self.collection_operation.save()

        self.count_trait()

        self.collection_operation.status = "completed"
        self.collection_operation.updated_date = datetime.datetime.utcnow()
        self.collection_operation.completed_date = datetime.datetime.utcnow()
        self.collection_operation.save()


class RandomAfterImageGenerator(SimpleImageGenerator):
    def generate(self, counter, until, layers):
        component_layers = []
        for l in layers.values():
            component_layers.append(list(l.values()))

        sample_layers = [list(range(0, len(l))) for k, l in layers.items()]

        products = itertools.product(*sample_layers)
        possible_components = list(products)
        random.shuffle(possible_components)

        for i in range(counter + 1, until + 1):
            j = 0
            while j < self.MAX_TRY:
                # print("len", len(possible_components))
                if len(possible_components) == 0:
                    print("out of range", possible_components)
                    return

                random_components = random.choice(possible_components)

                components = []
                is_remove = False
                for k, l in enumerate(random_components):
                    com = component_layers[k][l]

                    # print("->c", com)
                    if com["count"] + 1 > com["quota"]:
                        # print("over remove")
                        is_remove = True
                        break

                    if com["component"]:
                        components.append(com["component"])

                # print("r", random_components)
                # print("c", components)
                if is_remove or not self.is_valide_dna(components):
                    # print("remove")
                    possible_components.remove(random_components)
                    continue

                for k, l in enumerate(random_components):
                    com = component_layers[k][l]
                    com["count"] += 1

                print(f"random-after -> create image {i}")
                self.create_image(i, components)
                possible_components.remove(random_components)
                break


def generate(collection_operation):
    print("Random with", collection_operation.parameters.get("generated_type"))

    operation = None
    generated_type = collection_operation.parameters.get("generated_type")
    if generated_type == "normal-random":
        operation = SimpleImageGenerator(collection_operation)
    if generated_type == "random-after":
        operation = RandomAfterImageGenerator(collection_operation)

    if operation:
        operation.run()


def count_trait(collection_operation):
    operation = SimpleImageGenerator(collection_operation)
    collection_operation.status = "trait-counting"
    collection_operation.updated_date = datetime.datetime.utcnow()
    collection_operation.save()

    operation.count_trait()

    collection_operation.status = "completed"
    collection_operation.updated_date = datetime.datetime.utcnow()
    collection_operation.completed_date = datetime.datetime.utcnow()
    collection_operation.save()


def shake_token_id(collection_operation):
    operation = SimpleImageGenerator(collection_operation)
    collection_operation.status = "shaking-token-id"
    collection_operation.updated_date = datetime.datetime.utcnow()
    collection_operation.save()

    operation.shake_token_id()

    collection_operation.status = "completed"
    collection_operation.updated_date = datetime.datetime.utcnow()
    collection_operation.completed_date = datetime.datetime.utcnow()
    collection_operation.save()
