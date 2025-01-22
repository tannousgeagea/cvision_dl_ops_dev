from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

def test_azure_connection_with_connection_string(connection_string: str, container_name: str, file_name: str):
    """
    Test Azure Blob Storage connection and check if a file exists in the container using a connection string.

    :param connection_string: Azure Storage connection string.
    :param container_name: Name of the Azure Blob Storage container.
    :param file_name: File name (path) to check in the container.
    :return: True if the file exists, False otherwise.
    """
    try:
        # Create BlobServiceClient using the connection string
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Get the container client
        container_client = blob_service_client.get_container_client(container_name)

        # Check if the file exists
        blob_client = container_client.get_blob_client(file_name)
        if blob_client.exists():
            print(f"File '{file_name}' exists in the container '{container_name}'.")
            print(blob_client.url)
            return True
        else:
            print(f"File '{file_name}' does not exist in the container '{container_name}'.")
            return False

    except ResourceNotFoundError:
        print(f"Container '{container_name}' or file '{file_name}' not found.")
        return False
    except Exception as e:
        print(f"Error connecting to Azure Blob Storage: {e}")
        return False

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

def list_blobs_in_container(connection_string: str, container_name: str):
    """
    List all blobs inside a specified container in Azure Blob Storage.

    :param connection_string: Azure Storage connection string.
    :param container_name: Name of the Azure Blob Storage container.
    :return: List of blob names or an error message.
    """
    try:
        # Create BlobServiceClient using the connection string
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Get the container client
        container_client = blob_service_client.get_container_client(container=container_name)

        print(container_client.exists())

        # Check if the container exists
        if not container_client.exists():
            print(f"Container '{container_name}' does not exist.")
            return []

        # List all blobs in the container
        blob_list = container_client.list_blobs()
        blobs = [blob.name for blob in blob_list]
        
        print(f"Blobs in container '{container_name}':")
        for blob_name in blobs:
            print(f"- {blob_name}")

        return blobs

    except ResourceNotFoundError:
        print(f"Container '{container_name}' not found.")
        return []
    except Exception as e:
        print(f"Error listing blobs: {e}")
        return []



if __name__ == "__main__":
    # Azure Storage details
    import os
    AZURE_ACCOUNT_NAME = "wacoreblob"
    AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
    AZURE_CONTAINER = "cvisionops/media"
    AZURE_URL_EXPIRATION_SECS = 3600 

    AZURE_CONNECTION_STRING = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={AZURE_ACCOUNT_NAME};"
        f"AccountKey={AZURE_ACCOUNT_KEY};"
        f"EndpointSuffix=core.windows.net;"
        # f"BlobEndpoint=https://wacoreblob.blob.core.windows.net/cvisionops"
    )

    # # Test connection and file existence
    file_exists = test_azure_connection_with_connection_string(AZURE_CONNECTION_STRING, AZURE_CONTAINER, "images/AMK_gate03_front_2024-12-20_09-59-55_31c76ed8-91b0-4e3e-8884-8047920be83c.jpg")
    print(f"File exists: {file_exists}")
    
    # blobs = list_blobs_in_container(AZURE_CONNECTION_STRING, ".")
