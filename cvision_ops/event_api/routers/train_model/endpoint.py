# routes/models.py
import time
import django
django.setup()
from datetime import datetime
from typing import Callable, Optional
from fastapi import Request, Response, Header
from fastapi import APIRouter, HTTPException
from fastapi.routing import APIRoute
from typing import List, Literal
from pydantic import BaseModel
from typing_extensions import Annotated
from projects.models import Version
from ml_models.models import ModelVersion, Model
from training.models import TrainingSession
from event_api.tasks.train_model.core import train_model

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
    prefix="/api/v1",
    tags=["Training"],
    route_class=TimedRoute,
    responses={404: {"description": "Not found"}},
)

class TrainRequest(BaseModel):
    dataset_version_id: int
    config: Optional[dict] = {}

@router.post("/models/{model_id}/train")
def trigger_training(
    model_id: int, 
    body: TrainRequest,
    x_request_id: Annotated[Optional[str], Header()] = None,
    ):
    try:
        model = Model.objects.get(id=model_id)
        dataset = Version.objects.get(id=body.dataset_version_id)

        last_version = ModelVersion.objects.filter(model=model).order_by("-version").first()
        version_number = int(last_version.version) + 1 if last_version else 1

        model_version = ModelVersion.objects.create(
            model=model,
            version=version_number,
            dataset_version=dataset,
            config=body.config,
            status="training",
        )

        TrainingSession.objects.create(model_version=model_version)
        task = train_model.apply_async(args=(model_version.id, ), task_id=x_request_id)

        return {
            "message": "Training triggered",
            "model_version_id": model_version.id,
            "training_session_id": model_version.training_session.id,
            "task_id": task.id,
        }

    except (Model.DoesNotExist, Version.DoesNotExist):
        raise HTTPException(404, "Model or dataset not found")
    except Exception as e:
        raise HTTPException(500, str(e))
