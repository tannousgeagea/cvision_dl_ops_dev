
import os
import io
import uuid
import time
import zipstream
from PIL import Image
from typing_extensions import Annotated
from fastapi import APIRouter, HTTPException, Query, Header
from fastapi.routing import APIRoute
from fastapi import Request, Response
from typing import Callable, Optional, Literal
from django.core.files.base import ContentFile
from starlette.responses import StreamingResponse, FileResponse, RedirectResponse
from projects.models import Version, VersionImage
from annotations.models import Annotation
from django.core.files.storage import default_storage
from common_utils.data.annotation.core import format_annotation, read_annotation
from common_utils.progress.core import track_progress

def compress_image(path, quality=75):
    """Compress image and return bytes."""
    with default_storage.open(path, 'rb') as f:
        img = Image.open(f)
        img_io = io.BytesIO()
        img.convert('RGB').save(img_io, format='JPEG', optimize=True, quality=quality)
        img_io.seek(0)
        return img_io.read()

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


def get_cached_zip_path(cached_zip_path) -> str:
    """Return the cached zip file path if it exists, else an empty string."""
    if os.getenv("CACHE_ZIP_PATH") == "azure":
        if default_storage.exists(cached_zip_path):
            return cached_zip_path
    else:
        if os.path.exists(cached_zip_path):
            return cached_zip_path
    return ""

def generate_zip_stream(version: Version, annotation_format: str):
    """
    Generate a streaming zip file for a given version with annotations converted to the desired format.
    This function uses zipstream to build the zip file on the fly.

    Args:
        version (Version): The version instance.
        annotation_format (str): Desired annotation format (e.g., "yolo", "custom", etc.).

    Returns:
        zipstream.ZipFile: An iterable zip file stream.
    """
    z = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED, allowZip64=True)
    # z.write("start.txt", "Processing started...")
    version_images = VersionImage.objects.filter(version=version)

    for i, vi in enumerate(version_images):
        proj_img = vi.project_image
        prefix = proj_img.mode.mode if proj_img.mode else "default"
        image_path = proj_img.image.image_file.name
        image_filename = f"{os.path.basename(proj_img.image.image_file.name)}.jpg"
        def file_iterator(path):
            with default_storage.open(path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
        
        if not default_storage.exists(image_path):
            continue

        try:
            # compressed_image = compress_image(image_path, quality=65)
            print(image_path)
            file_iter = file_iterator(image_path)
            z.write_iter(f"{prefix}/images/{image_filename}", file_iter)
        except Exception as e:
            print(f"Error compressing or adding original image {image_filename}: {e}")

        annotations = Annotation.objects.filter(project_image=proj_img, is_active=True)
        annotation_str = "".join([format_annotation(ann, format=annotation_format) for ann in annotations])
        annotation_bytes = annotation_str.encode('utf-8')
        z.writestr(f"{prefix}/labels/{os.path.basename(proj_img.image.image_file.name)}.txt", annotation_bytes)

        augmentations = vi.augmentations.all()
        for aug in augmentations:
            # Create filenames that include the augmentation name.
            aug_image_filename = f"{os.path.basename(aug.augmented_image_file.name)}.jpg"
            aug_annotation_filename = f"{os.path.basename(aug.augmented_image_file.name)}.txt"
            
            if aug.augmented_image_file:
                try:
                    z.write_iter(f"{prefix}/images/{aug_image_filename}", file_iterator(aug.augmented_image_file.name))
                except Exception as e:
                    print(f"Error adding augmented image for {os.path.basename(proj_img.image.image_file.name)}: {e}")
            
            if aug.augmented_annotation:
                # Convert annotation dictionary to string using read_annotation helper.
                annotation_str = "".join([
                    read_annotation(bbox=bbox, label=label, format=annotation_format)
                    for bbox, label in zip(aug.augmented_annotation['bboxes'], aug.augmented_annotation['labels'])
                ])
                z.writestr(f"{prefix}/labels/{aug_annotation_filename}", annotation_str.encode("utf-8"))
    return z


@router.get("/versions/{version_id}/download", tags=["Versions"])
def download_version(
    version_id: int, 
    format:Literal["yolo", "custom", "coco"] = Query("yolo", description="Desired annotation format"),
    x_request_id: Annotated[Optional[str], Header()] = None,
    ):
    """
    On-demand endpoint to download a version's images with annotations in a preferred format.
    
    - The version images remain stored in Azure.
    - Annotations are converted to the requested format on the fly.
    - The zip archive is built dynamically and streamed back to the user.
    
    **Query Parameters:**
      - **format**: Desired annotation format (default is "yolo").
    
    **Response:**
      - A streaming zip file containing:
          - For each image: the image file (under `{mode}/images/`) and its corresponding annotation file (under `{mode}/labels/`).
    """
    try:
        version = Version.objects.get(id=version_id)
    except Version.DoesNotExist:
        raise HTTPException(status_code=404, detail="Version not found")
    
    task_id = x_request_id if x_request_id else str(uuid.uuid4())
    filename = f"{version.project.name}.v{version.version_number}.{format}.zip"
    local_path = "/tmp/versions"
    os.makedirs(local_path, exist_ok=True)

    local_zip_path = f"versions/{filename}" if os.getenv("CACHE_ZIP_PATH") == "azure" else os.path.join(local_path, filename)
    cached_zip_path = get_cached_zip_path(local_zip_path)
    if cached_zip_path:
        if os.getenv("CACHE_ZIP_PATH") == "azure":
            return {"url": version.version_file.url}
        else:
            return FileResponse(
                cached_zip_path,
                media_type="application/zip",
                filename=filename
            )
    
    track_progress(task_id=task_id, percentage=0, status="Zipping Files ...")
    zip_stream = generate_zip_stream(version, annotation_format=format)
    track_progress(task_id=task_id, percentage=100, status="Zipping Files Completed")

    track_progress(task_id=task_id, percentage=0, status="Generating Zip file ...")
    if os.getenv("CACHE_ZIP_PATH") == "azure":
        version_zip_rel_path = f"versions/{filename}"
        zip_buffer = io.BytesIO()
        for chunk in zip_stream:
            zip_buffer.write(chunk)
        zip_buffer.seek(0)

        zip_path = default_storage.save(version_zip_rel_path, ContentFile(zip_buffer.getvalue()))
        version.version_file = zip_path
        version.save(update_fields=["version_file"])
        track_progress(task_id=task_id, percentage=100, status="Completed")

        return {"url": version.version_file.url}
    else:
        with open(local_zip_path, "wb") as f:
            for chunk in zip_stream:
                f.write(chunk)

        track_progress(task_id=task_id, percentage=100, status="Completed")
        return FileResponse(
            local_zip_path,
            media_type="application/zip",
            filename=filename)
