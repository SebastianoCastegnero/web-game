import random

from src.database.storage_item import StorageItem


class InMemoryStorage:
    """
    InMemory database to store game items: secret words and hint images.
    """

    def __init__(self):
        self.storage: list[StorageItem] = []

    def add(self, item: StorageItem) -> str:
        """ Store a secret word with the image."""
        self.storage.append(item)
        return str(len(self.storage) - 1)  # last index in the list

    def get_all_secrets(self) -> list[str]:
        """ Get all secret words saved so far. """
        return [item.secret_word for item in self.storage]

    def has_index(self, index: str) -> bool:
        """ Does the database contain the given index? """
        return index.isnumeric() and 0 <= int(index) < len(self.storage)

    def get_random_item_index(self) -> str:
        """ Get an index of a random secret image."""
        return str(random.randint(0, len(self.storage) - 1))

    def get_item_by_index(self, index: str) -> StorageItem:
        """
        Return the item by the index from the database.
        """
        return self.storage[int(index)]

    def is_empty(self) -> bool:
        """
        Is the database empty?
        """
        return not self.storage