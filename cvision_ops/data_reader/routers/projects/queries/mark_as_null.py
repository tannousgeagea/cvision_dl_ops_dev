import time
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import Callable, Optional
from fastapi import Request
from fastapi import Response
from fastapi.routing import APIRoute, APIRouter
from django.db import transaction
from projects.models import (
    Project, 
    ProjectImage,
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
    "/projects/{project_id}/mark_as_null", methods=["POST"], tags=["Projects"]
    )
def mark_image_as_null(project_id: str, image_id: Optional[str]=None, marked_as_null: Optional[bool] = None):
    try:
        project = Project.objects.filter(name=project_id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found")

        if image_id:
            project_image = ProjectImage.objects.filter(project=project, image__image_id=image_id).first()

            if marked_as_null:
                project_image.status = "reviewed"
                project_image.reviewed = True
                project_image.marked_as_null = True
            else:
                project_image.status = "annotated"

            project_image.save()
            return {"message": f"Image marked as null", "success": True}
        
        
        project_images =  ProjectImage.objects.filter(project=project, status="annotated")   
        if not project_images:
            raise HTTPException(status_code=404, detail="Image not found in project")

        project_images.update(status="reviewed", reviewed=True, marked_as_null=True)
        return {"message": f"{len(project_images)} Images marked as Null!", "success": True}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
