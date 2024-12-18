from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Image

@admin.register(Image)
class ImageAdmin(ModelAdmin):
    list_display = ('image_name', 'image_file', 'created_at', 'annotated', 'processed')
    search_fields = ('image_name', )
    list_filter = ('annotated', 'processed','created_at', 'source_of_origin')