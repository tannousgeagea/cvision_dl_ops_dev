
import time
import django
django.setup()
from celery import shared_task
from django.utils import timezone
from training.models import ModelVersion

@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5}, ignore_result=True,
             name='train_model:execute')
def train_model(self, version_id:str):
    try:
        version = ModelVersion.objects.get(id=version_id)
        session = version.training_session

        # Start training
        session.status = "running"
        session.started_at = timezone.now()
        session.save()

        # Simulated training steps
        for i in range(10):
            time.sleep(10)
            session.progress = round((i + 1) * 10, 1)
            session.logs +=  f"Epoch {i}: training in progress" + "\n"
            session.save()

        # Simulate metrics and final state
        version.metrics = {
            "accuracy": 0.93,
            "f1Score": 0.91
        }
        version.status = "trained"
        version.save()

        session.status = "completed"
        session.completed_at = timezone.now()
        session.save()

    except Exception as e:
        if "version" in locals():
            version.status = "failed"
            version.save()
        if "session" in locals():
            session.status = "failed"
            session.error_message = str(e)
            session.completed_at = timezone.now()
            session.save()
        raise