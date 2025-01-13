import os
import math
import uuid
import time
import django
import shutil
django.setup()
from django.db.models import Q
from datetime import datetime, timedelta
from datetime import time as dtime
from datetime import date, timezone
from typing import Callable, Optional, Dict, AnyStr, Any
from fastapi import Request
from fastapi import Response
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.routing import APIRoute
from fastapi import status
from pathlib import Path
from pydantic import BaseModel


from images.models import Image
from tenants.models import (
    Tenant,
    Plant,
    EdgeBox,
)
from projects.models import (
    Project,
    ProjectImage,
)

from annotations.models import (
    Annotation
)


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

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
    "/projects/{project_name}/images", methods=["GET"], tags=["Projects"]
)
def get_project_images(
    response: Response,
    project_name:str,
    annotated:bool=False,
    reviewed:bool=False,
    items_per_page:int=50,
    page:int=1,
    ):
    results = {}
    try:
        
        project = Project.objects.filter(name=project_name)
        if not project:
            results['error'] = {
                'status_code': "not found",
                "status_description": f"Project {project_name} not found",
                "detail": f"Project {project_name} not found",
            }
            
            response.status_code = status.HTTP_404_NOT_FOUND
            return results
        
        project = project.first()
        
        if page < 1:
            page = 1
        
        if reviewed:
            annotated = True
            
        images = ProjectImage.objects.filter(project=project, annotated=annotated, reviewed=reviewed)
        data = []
        for image in images[(page - 1) * items_per_page:page * items_per_page]:
            annotation = Annotation.objects.filter(project_image=image, is_active=True)
            data.append(
                {
                    'image_id': image.image.image_id,
                    'image_name': image.image.image_name,
                    'image_url': 'http://localhost:81' + image.image.image_file.url,
                    'created_at': image.image.created_at.strftime(DATETIME_FORMAT),
                    'plant': image.image.sensorbox.edge_box.plant.plant_name if image.image.sensorbox else None,
                    'edge_box': image.image.sensorbox.sensor_box_name if image.image.sensorbox else None,
                    'location': image.image.sensorbox.edge_box.edge_box_location if image.image.sensorbox else None,
                    'sub_location': image.image.sensorbox.sensor_box_location if image.image.sensorbox else None,
                    'annotated': image.annotated,
                    'reviewed': image.reviewed,
                    "annotations": [
                        {
                             "class_id": ann.annotation_class.class_id,
                             "class_name": ann.annotation_class.name,
                             "xyxyn": ann.data,
                        } for ann in annotation
                    ]
                }              
            )
            
        total_record = len(images)
        results = {
            "total_record": total_record,
            "pages": math.ceil(total_record / items_per_page),
            'unannotated': len(ProjectImage.objects.filter(project=project, annotated=False, reviewed=False)),
            'annotated': len(ProjectImage.objects.filter(project=project, annotated=True, reviewed=False)),
            'reviewed': len(ProjectImage.objects.filter(project=project, annotated=True, reviewed=True)),
            'data': data,
        }
    
    except HTTPException as e:
        results['error'] = {
            "status_code": "not found",
            "status_description": "Request not Found",
            "detail": f"{e}",
        }
        
        response.status_code = status.HTTP_404_NOT_FOUND
    
    except Exception as e:
        results['error'] = {
            'status_code': 'server-error',
            "status_description": f"Internal Server Error",
            "detail": str(e),
        }
        
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return results 