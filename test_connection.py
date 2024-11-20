from azure.storage.blob import BlobServiceClient
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG)

AZURE_ACCOUNT_NAME = "wacoreblob"
AZURE_ACCOUNT_KEY = "sp=rcw&st=2024-11-20T10:49:39Z&se=2024-12-06T18:49:39Z&spr=https&sv=2022-11-02&sr=c&sig=FnpYkqVONGRwssglNjzH0WJFxX2yMhAArrF93L4NKxs%3D"
AZURE_CONTAINER = "cvisionops"
AZURE_CONNECTION_STRING = (
    f"DefaultEndpointsProtocol=https;"
    f"AccountName={AZURE_ACCOUNT_NAME};"
    f"AccountKey={AZURE_ACCOUNT_KEY};"
    f"EndpointSuffix=core.windows.net"
)


print(AZURE_CONNECTION_STRING)
# Connect to Azure Blob Storage
try:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(container=AZURE_CONTAINER)


    print(container_client.account_name)
    # List blobs in the container
    print("Blobs in the container:")
    for blob in container_client.list_blobs():
        print(blob.name)

except Exception as e:
    print(f"Error: {e}")