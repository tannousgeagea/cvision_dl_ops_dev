import os
import zipfile
import shutil
import time
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import Callable
from fastapi import Request
from fastapi import Response
from fastapi.routing import APIRoute, APIRouter
from django.db import transaction
from django.core.files.base import ContentFile
from storages.backends.azure_storage import AzureStorage
from starlette.responses import FileResponse
from common_utils.azure_manager.core import AzureManager
from common_utils.data.annotation.core import save_annotations_into_txtfile
from projects.models import (
    Project, 
    ProjectImage, 
    Version, 
    VersionImage
)
from annotations.models import Annotation

class TimedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            print(f"route duration: {duration}")
            print(f"route response: {response}")
            print(f"route response headers: {response.headers}")
            return response

        return custom_route_handler


router = APIRouter(
    route_class=TimedRoute,
    responses={404: {"description": "Not found"}},
)

@router.api_route(
    "/projects/{project_id}/versions", methods=["POST"], tags=["Versions"], status_code=status.HTTP_201_CREATED
    )
def create_version(
    response:Response,
    project_id: str,
    ):
    """
    Create a new version for a project by associating all reviewed images with the version.
    """
    try:
        # Fetch the project
        project = Project.objects.filter(name=project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found")

        # Determine the next version number
        project = project.first()
        last_version = Version.objects.filter(project=project).order_by('-version_number').first()
        next_version_number = last_version.version_number + 1 if last_version else 1
        images = ProjectImage.objects.filter(project=project, status="dataset")[:50]

        if not images.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="No reviewed images available to create a version"
            )

        # Start transaction
        with transaction.atomic():
            # Create a new version
            new_version = Version.objects.create(
                project=project,
                version_number=next_version_number,
                version_name=f"v{next_version_number}",
                created_at=datetime.now()
            )

            # Associate images with the new version
            version_images = [
                VersionImage(version=new_version, project_image=img)
                for img in images
            ]
            VersionImage.objects.bulk_create(version_images)
            
        if os.getenv('DJANGO_STORAGE', 'local') == 'azure':
            azure_manager = AzureManager()
            azure_manager.zip_dataset(version_images, version=new_version)
        else:
            folder_name = f"{new_version.project.name}.v{new_version.version_number}"
            base_dir = f"/tmp/{folder_name}"
            os.makedirs(f"{base_dir}/train/images", exist_ok=True)
            os.makedirs(f"{base_dir}/valid/images", exist_ok=True)
            
            for image in images:
                prefix = image.project_image.mode.mode
                image_path = image.project_image.image.image_file.path
                annotations = Annotation.objects.filter(
                    project_image=image.project_image,
                    is_active=True
                    )
                save_annotations_into_txtfile(annotations, image.project_image.image.image_name, dest=f"{base_dir}/{prefix}")
                os.symlink(image_path, f"{base_dir}/{prefix}/images/{image.project_image.image.image_name}.jpg")

            # Zip the folder
            zip_file_path = f"/tmp/{folder_name}.zip"
            with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(base_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, base_dir)
                        zipf.write(file_path, arcname)

            with open(zip_file_path, "rb") as zipf:
                file_content = zipf.read()
                new_version.version_file.save(f"{folder_name}.zip", ContentFile(file_content))

            shutil.rmtree(base_dir)
            os.remove(zip_file_path)

        return {"message": f"Version v{next_version_number} created successfully", "version_id": new_version.id, "version_number": new_version.version_number}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
