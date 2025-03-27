import zipstream
import os
import time
from fastapi import APIRouter, HTTPException, Query
from fastapi.routing import APIRoute
from fastapi import Request, Response
from typing import Callable
from starlette.responses import StreamingResponse
from projects.models import Version, VersionImage
from annotations.models import Annotation
from django.core.files.storage import default_storage
from common_utils.data.annotation.core import format_annotation, read_annotation


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
    z = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)
    version_images = VersionImage.objects.filter(version=version)

    for vi in version_images:
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
        
        z.write_iter(f"{prefix}/images/{image_filename}", file_iterator(image_path))        
        annotations = Annotation.objects.filter(project_image=proj_img, is_active=True)
        annotation_str = "".join([format_annotation(ann, format=annotation_format) for ann in annotations])
        annotation_bytes = annotation_str.encode('utf-8')
        z.writestr(f"{prefix}/labels/{os.path.basename(proj_img.image.image_file.name)}.txt", annotation_bytes)

        augmentations = vi.augmentations.all()
        for aug in augmentations:
            # Create filenames that include the augmentation name.
            aug_image_filename = f"{os.path.basename(aug.augmented_image_file.name)}.jpg"
            aug_annotation_filename = f"{os.path.basename(aug.augmented_image_file.name)}.txt"
            
            # Read the augmented image file using the storage backend.
            if aug.augmented_image_file:
                try:
                    with default_storage.open(aug.augmented_image_file.name, 'rb') as f:
                        aug_image_bytes = f.read()
                    z.writestr(f"{prefix}/images/{aug_image_filename}", aug_image_bytes)
                except Exception as e:
                    # Log the error and continue
                    print(f"Error adding augmented image for {os.path.basename(proj_img.image.image_file.name)}: {e}")
            
            # Add the augmented annotation (if available)
            if aug.augmented_annotation:
                annotation_str = "".join([read_annotation(bbox=bbox, label=label, format=annotation_format) for bbox, label in zip(aug.augmented_annotation['bboxes'], aug.augmented_annotation['labels'])])
                z.writestr(f"{prefix}/labels/{aug_annotation_filename}", annotation_str.encode("utf-8"))
    return z


@router.get("/versions/{version_id}/download", tags=["Versions"])
def download_version(version_id: int, format: str = Query("yolo", description="Desired annotation format")):
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
    
    zip_stream = generate_zip_stream(version, annotation_format=format)
    
    filename = f"{version.project.name}.v{version.version_number}.{format}.zip"
    response = StreamingResponse(zip_stream, media_type="application/zip")
    response.headers["Transfer-Encoding"] = "chunked"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
