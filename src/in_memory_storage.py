import random
from typing import Optional

class InMemoryStorage:
    def __init__(self):
        self.storage = []

    def add_word(self, secret_word: str) -> None:
        """ Store a secret word."""
        self.storage.append(secret_word)

    def get_all_words(self):
        """ Get all words saved so far. """
        return self.storage
    
    def get_random_word_index(self) -> Optional[int]:
        """ Get an index of a random secret word."""
        if not self.storage:
            return None  # no words saved - nothing to return
        return random.randint(0, len(self.storage) - 1)

    def get_word_by_index(self, index: int) -> Optional[str]:
        """
        Given the index in the storage, return the secret word by this index.
        """
        if not (0 <= index < len(self.storage)):
            return None  # index out of range - nothing to return
        return self.storage[index]
