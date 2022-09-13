from src.in_memory_storage import InMemoryStorage, StorageItem


def test_get_random_index_when_one_item():
    storage = InMemoryStorage()
    storage.add(StorageItem(
        image_content_type="text/plain",
        image_bytes=b"not important",
        secret_word="cat",
    ))
    # when there's only one item, the only index we can get from the method is 0
    assert storage.get_random_item_index() == 0