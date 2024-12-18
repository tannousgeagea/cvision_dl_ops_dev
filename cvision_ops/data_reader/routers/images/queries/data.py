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
    "/images", methods=["GET"], tags=["Images"]
)
def get_images(
    response: Response,
    image_id:str=None,
    plant:str=None,
    location:str=None,
    created_at:datetime=None,
    ):
    results = {}
    try:
        if image_id:
            image = Image.objects.get(image_id=image_id)
            return {
                "data": [
                    { 
                        'image_id': image.image_id,
                        'image_name': image.image_name,
                        'image_url': image.image_file.url,
                        'created_at': image.created_at.strftime(DATETIME_FORMAT),
                        'plant': image.sensorbox.edge_box.plant.plant_name if image.sensorbox else None,
                        'edge_box': image.sensorbox.sensor_box_name if image.sensorbox else None,
                        'location': image.sensorbox.edge_box.edge_box_location if image.sensorbox else None,
                        'sub_location': image.sensorbox.sensor_box_location if image.sensorbox else None,     
                    }
                ]
            }
        
        lookup_filter = Q()
        if plant:
            plant = Plant.objects.get(plant_name=plant)
            if location:
                lookup_filter &= Q(('sensorbox__edge_box__edge_box_location', location))
            else:
                lookup_filter &= Q(('sensorbox__edge_box__plant', plant))  
        if created_at:
            lookup_filter &= Q(('created_at__range', (created_at.replace(tzinfo=timezone.utc), datetime.combine(created_at, dtime.max).replace(tzinfo=timezone.utc))))
        
        images = Image.objects.filter(lookup_filter)
        results = {
            'data': [
                {
                    'image_id': image.image_id,
                    'image_name': image.image_name,
                    'image_url': image.image_file.url,
                    'created_at': image.created_at.strftime(DATETIME_FORMAT),
                    'plant': image.sensorbox.edge_box.plant.plant_name if image.sensorbox else None,
                    'edge_box': image.sensorbox.sensor_box_name if image.sensorbox else None,
                    'location': image.sensorbox.edge_box.edge_box_location if image.sensorbox else None,
                    'sub_location': image.sensorbox.sensor_box_location if image.sensorbox else None,
                } for image in images
            ]
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
