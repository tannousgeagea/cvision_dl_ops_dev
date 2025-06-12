# api/validation.py

import time
from fastapi import APIRouter, HTTPException
from ml_models.models import ModelVersion
from projects.models import VersionImage, ImageMode
from inferences.models import PredictionImageResult, PredictionOverlay
from common_utils.inference.utils import run_inference
from django.db import transaction

router = APIRouter()

@router.post("/validate-model/{model_version_id}")
def validate_model(model_version_id: int):
    try:
        model_version = ModelVersion.objects.get(id=model_version_id)
    except ModelVersion.DoesNotExist:
        raise HTTPException(status_code=404, detail="Model version not found")

    version = model_version.dataset_version
    mode = ImageMode.objects.get(mode="valid")
    version_images = VersionImage.objects.filter(version=version, project_image__mode=mode)
    created_results = 0

    for vi in version_images:
        image = vi.project_image.image
        dataset_version = vi.version 

        # Skip if already validated
        if PredictionImageResult.objects.filter(
            model_version=model_version,
            dataset_version=dataset_version,
            image=image
        ).exists():
            continue

        start_time  = time.time()
        predictions = run_inference(image=image.image_file.name, model_version_id=model_version_id)
        inference_time = time.time() - start_time

        with transaction.atomic():
            result = PredictionImageResult.objects.create(
                model_version=model_version,
                dataset_version=dataset_version,
                image=image,
                inference_time=round(inference_time, 4),
            )

            overlay_objs = [
                PredictionOverlay(
                    prediction_result=result,
                    class_label=pred["class_label"],
                    confidence=pred["confidence"],
                    bbox=pred.get("xyxyn"),
                    mask=pred.get("mask"),
                    overlay_type=pred.get("overlay_type", "bbox"),
                )
                for pred in predictions
            ]

            PredictionOverlay.objects.bulk_create(overlay_objs)
            created_results += 1

    return {
        "message": f"Validation completed for model version {model_version_id}",
        "total_images_processed": version_images.count(),
        "new_results_created": created_results
    }
