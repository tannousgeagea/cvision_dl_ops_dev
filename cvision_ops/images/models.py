from django.db import models
from tenants.models import EdgeBox

# Create your models here.
class ImageMode(models.Model):
    mode = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'image_mode'
        verbose_name_plural = 'Image Mode'
        
    def __str__(self):
        return self.mode

class Image(models.Model):
    image_id = models.CharField(max_length=255, unique=True)
    image_name = models.CharField(max_length=255, unique=True)
    image_file = models.ImageField(upload_to='images/')
    annotated = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    source_of_origin = models.CharField(max_length=255, null=True, blank=True)
    mode = models.ForeignKey(ImageMode, on_delete=models.CASCADE, blank=True, null=True)
    meta_info = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'image'
        verbose_name_plural = 'Images'
        
    def __str__(self):
        return self.image_name