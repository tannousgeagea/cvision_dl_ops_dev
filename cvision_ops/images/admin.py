from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ImageMode, Image

@admin.register(ImageMode)
class ImageModeAdmin(ModelAdmin):
    list_display = ('mode', 'description', 'created_at')
    search_fields = ('mode', 'description')
    list_filter = ('created_at',)

@admin.register(Image)
class ImageAdmin(ModelAdmin):
    list_display = ('image_name', 'image_file', 'created_at', 'annotated', 'processed', 'mode')
    search_fields = ('image_name', 'mode__mode')
    list_filter = ('annotated', 'processed', 'mode', 'created_at', 'source_of_origin')