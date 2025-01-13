import time
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import Callable
from fastapi import Request
from fastapi import Response
from fastapi.routing import APIRoute, APIRouter
from django.db import transaction
from projects.models import (
    Project, 
    ProjectImage, 
    Version, 
    VersionImage
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
    "/projects/{project_name}/versions", methods=["POST"], tags=["Projects"], status_code=status.HTTP_201_CREATED
    )
def create_version(
    response:Response,
    project_name: str,
    ):
    """
    Create a new version for a project by associating all reviewed images with the version.
    """
    try:
        # Fetch the project
        project = Project.objects.filter(name=project_name)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_name} not found")

        # Determine the next version number
        project = project.first()
        last_version = Version.objects.filter(project=project).order_by('-version_number').first()
        next_version_number = last_version.version_number + 1 if last_version else 1
        reviewed_images = ProjectImage.objects.filter(project=project, reviewed=True)

        if not reviewed_images.exists():
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
                created_at=datetime.now()
            )

            # Associate images with the new version
            version_images = [
                VersionImage(version=new_version, project_image=img)
                for img in reviewed_images
            ]
            VersionImage.objects.bulk_create(version_images)

        return {"message": f"Version v{next_version_number} created successfully", "version_id": new_version.id}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
