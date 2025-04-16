from jobs.models import Job


def update_job_status(job: Job):
    images = job.images.select_related("project_image").all()
    statuses = [img.project_image.status for img in images]

    if not job.assignee:
        job.status = "unassigned"
    elif all(s in ["reviewed", "dataset"] for s in statuses):
        job.status = "completed"
    elif all(s in ["annotated", "reviewed"] for s in statuses):
        job.status = "in_review"
    else:
        job.status = "assigned"

    job.save(update_fields=["status"])