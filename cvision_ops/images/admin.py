import io
import os
import zipfile

from django.contrib import admin
from unfold.admin import ModelAdmin
from django.http import HttpResponse
from .models import Image


@admin.action(description="Download selected images as a ZIP")
def download_selected_images(modeladmin, request, queryset):
    """
    Custom admin action to bundle the selected Image objects into a ZIP file
    and send it as a download to the browser.
    This approach uses file-like reading from the storage backend 
    (e.g., Azure Storage), so we don't rely on local file paths.
    """
    # Create an in-memory buffer to build the ZIP file
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for image_obj in queryset:
            if image_obj.image_file:
                # Open the file from the storage backend
                # and read its content into memory.
                file_name = os.path.basename(image_obj.image_file.name)
                with image_obj.image_file.open() as f:
                    file_content = f.read()
                
                # Write this file into the ZIP with a proper filename
                zip_file.writestr(file_name, file_content)

    # Move the buffer cursor to the beginning
    buffer.seek(0)

    # Build the HTTP response
    response = HttpResponse(buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="images.zip"'
    return response

@admin.register(Image)
class ImageAdmin(ModelAdmin):
    list_display = ('image_name', 'image_file', 'created_at', 'annotated', 'processed')
    search_fields = ('image_name', )
    list_filter = ('annotated', 'processed','created_at', 'source_of_origin', 'sensorbox__edge_box__plant', 'sensorbox__edge_box__edge_box_location')
    actions = [download_selected_images]