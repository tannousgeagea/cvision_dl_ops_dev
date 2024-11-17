import os
import math
import uuid
import time
import django
import shutil
django.setup()
from datetime import datetime, timedelta
from datetime import date, timezone
from typing import Callable, Optional, Dict, AnyStr, Any
from fastapi import Request
from fastapi import Response
from fastapi import APIRouter
from fastapi import Depends, Form, Body
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi import status
from fastapi import File, UploadFile
from pathlib import Path
from pydantic import BaseModel
from django.conf import settings
from utils.data.image import save_image

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
)

@router.api_route(
    "/images/metadata", methods=["GET"], tags=["Images"]
)
def get_images_metadata(response: Response):
    results = {}
    try:
        
        results = {
            'metadata': {
                'columns': []
            }
        }
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    

