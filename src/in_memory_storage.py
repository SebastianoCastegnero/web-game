import random
from dataclasses import dataclass

@dataclass(frozen=True)  # 'frozen' makes it immutable - always good by default
class StorageItem:
    image_url: str
    secret_word: str  # now only contains a secret word, but later we'll add an image here!

class InMemoryStorage:
    def __init__(self):
        self.storage: list[StorageItem] = []

    def add(self, item: StorageItem) -> None:
        self.storage.append(item)

    def get_all_secrets(self) -> list[str]:
        return [item.secret_word for item in self.storage]

    def has_index(self, index: int) -> bool:
        return 0 <= index < len(self.storage)

    def get_random_item_index(self) -> int:  # raises exception if empty
        return random.randint(0, len(self.storage) - 1)

    def get_item_by_index(self, index: int) -> StorageItem:  # raises exception if empty
        return self.storage[index]

    def is_empty(self) -> bool:
        return not self.storage
