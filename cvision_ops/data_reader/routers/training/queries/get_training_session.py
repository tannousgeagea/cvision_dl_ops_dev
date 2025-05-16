# routes/models.py
import time
from datetime import datetime
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi import APIRouter, HTTPException
from fastapi.routing import APIRoute
from typing import List
from pydantic import BaseModel
from training.models import TrainingSession

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

@router.get("/training-sessions/{session_id}")
def get_training_session(session_id: int):
    try:
        session = TrainingSession.objects.select_related("model_version").get(id=session_id)
        return {
            "model_version": session.model_version.id,
            "status": session.status,
            "progress": session.progress,
            "log_path": session.log_path,
            "error_message": session.error_message,
            "started_at": session.started_at,
            "completed_at": session.completed_at
        }
    except TrainingSession.DoesNotExist:
        raise HTTPException(404, "Session not found")
