import dataclasses
import os
import random
import uuid

from src.database.storage_item import StorageItem
from azure.cosmos import exceptions, CosmosClient, PartitionKey, ContainerProxy


class CosmosStorage:
    """
    Cosmos DB database to store game items: secret words and hint images.
    """

    def __init__(self, container: ContainerProxy):
        self.container = container

    @classmethod
    def from_parameters(cls, account_endpoint, account_key, db_name, container_name):
        """ Create storage from account credentials and db/container names """
        client = CosmosClient(account_endpoint, account_key)

        try:
            database = client.create_database(id=db_name)
        except exceptions.CosmosResourceExistsError:  # db already exists
            database = client.get_database_client(database=db_name)

        try:
            container = database.create_container(
                id=container_name, partition_key=PartitionKey(path="/id")  # partition by ID
            )
        except exceptions.CosmosResourceExistsError:  # container already exists
            container = database.get_container_client(container_name)

        return cls(container)

    @classmethod
    def from_env(cls):
        """ Create storage from environment variables """
        return cls.from_parameters(
            account_endpoint=os.environ["COSMOS_ACCOUNT_ENDPOINT"],
            account_key=os.environ["COSMOS_ACCOUNT_KEY"],
            db_name=os.environ["COSMOS_DB_NAME"],
            container_name=os.environ["COSMOS_CONTAINER_NAME"],
        )
    def add(self, item: StorageItem) -> str:
        """
        Store a secret word with the image.
        Return the id of the created item.
        """
        item_as_dict = dataclasses.asdict(item)
        cosmos_item = {
            "id": str(uuid.uuid4()),  # random id
            "storage_item": item_as_dict,
        }
        self.container.upsert_item(cosmos_item)
        return cosmos_item['id']

    def get_all_secrets(self) -> list[str]:
        """ Get all secret words saved so far. """
        return [
            cosmos_item['storage_item']['secret_word']
            for cosmos_item in self.container.read_all_items()
        ]

    def has_index(self, index: str) -> bool:
        """ Does the database contain the given index? """
        try:
            self.container.read_item(index, partition_key=index)
            return True
        except exceptions.CosmosHttpResponseError:
            return False

    def get_random_item_index(self) -> str:
        """ Get an index of a random secret image."""
        all_ids = [
            cosmos_item['id']
            for cosmos_item in self.container.read_all_items()
        ]
        return random.choice(all_ids)

    def get_item_by_index(self, index: str) -> StorageItem:
        """
        Return the item by the index from the database.
        """
        cosmos_item = self.container.read_item(index, partition_key=index)
        return StorageItem(
            image_url=cosmos_item['storage_item']['image_url'],
            secret_word=cosmos_item['storage_item']['secret_word'],
        )

    def is_empty(self) -> bool:
        """
        Is the database empty?
        """
        first_items = list(self.container.read_all_items(max_item_count=1))
        return first_items == []