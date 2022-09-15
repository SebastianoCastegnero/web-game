import os
import uuid
from azure.storage.blob import BlobServiceClient, ContentSettings


class BlobStorage: # pylint: disable=too-few-public-methods
    """
        Blob store to store secret words.
    """

    def __init__(self):
        self.account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME', '')
        self.account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY', '')
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key};EndpointSuffix=core.windows.net"

        self.client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = 'images-to-guess'
        self.container_client = self.client.get_container_client(self.container_name)
        if not self.container_client.exists():
            self.container_client.create_container(timeout=1000, public_access ='container')

    def upload_image(self, image_bytes, content_type) -> str:
        """Store an image in a blob and returns the name of the blob"""
        file_name = str(uuid.uuid4())
        blob_client = self.container_client.get_blob_client(file_name)
        blob_client.upload_blob(
            image_bytes,
            blob_type="BlockBlob",
            content_settings=ContentSettings(content_type=content_type),
        )
        image_url = f'https://{self.account_name}.blob.core.windows.net/{self.container_name}/{file_name}'

        return image_url
