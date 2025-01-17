import os
import zipfile
import time
import django
import shutil
django.setup()
from django.db.models import Q
from datetime import datetime, timedelta
from typing import Callable, Dict, AnyStr, Any
from fastapi import Request
from fastapi import Response
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.routing import APIRoute
from fastapi import status
from pathlib import Path
from pydantic import BaseModel
from starlette.responses import FileResponse
from projects.models import (
    Version, 
    ProjectImage, 
    Project,
    VersionImage,
)

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
    "/projects/{project_id}/versions/{version_id}/download", methods=["GET"], tags=["Projects"]
    )
def download_version(project_id: str, version_id: int):
    try:
        # Fetch version and associated images
        project = Project.objects.filter(name=project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found."
            )

        version = Version.objects.filter(project=project, version_number=version_id).first()
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")

        # Fetch images and split them
        train_images = VersionImage.objects.filter(version=version, project_image__mode__mode="train").all()
        valid_images = VersionImage.objects.filter(version=version, project_image__mode__mode="valid").all()

        # Create folder structure
        folder_name = f"{version.project.name}.v{version.version_number}"
        base_dir = f"/tmp/{folder_name}"
        os.makedirs(f"{base_dir}/train/images", exist_ok=True)
        os.makedirs(f"{base_dir}/valid/images", exist_ok=True)

        # Save images in respective folders
        for image in train_images:
            image = image.project_image.image
            image_path = image.image_file.path # Assuming `file_path` is the field storing the file's path
            os.symlink(image_path, f"{base_dir}/train/images/{image.image_name}.jpg")

        for image in valid_images:
            image = image.project_image.image
            image_path = image.image_file.path
            os.symlink(image_path, f"{base_dir}/valid/images/{image.image_name}.jpg")

        # Zip the folder
        zip_file_path = f"/tmp/{folder_name}.zip"
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(base_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, base_dir)
                    zipf.write(file_path, arcname)

        shutil.rmtree(base_dir)
        return FileResponse(zip_file_path, filename=f"{folder_name}.zip", media_type="application/zip")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
