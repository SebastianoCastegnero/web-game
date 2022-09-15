from dataclasses import dataclass

@dataclass(frozen=True)  # 'frozen' makes it immutable - always good by default
class StorageItem:
    image_url: str
    secret_word: str  # now only contains a secret word, but later we'll add an image here!