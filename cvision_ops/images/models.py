from django.db import models
from tenants.models import EdgeBox, SensorBox

# Create your models here.
class Image(models.Model):
    image_id = models.CharField(max_length=255, unique=True)
    image_name = models.CharField(max_length=255, unique=True)
    image_file = models.ImageField(upload_to='images/')
    annotated = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    source_of_origin = models.CharField(max_length=255, null=True, blank=True)
    meta_info = models.JSONField(null=True, blank=True)
    sensorbox = models.ForeignKey(SensorBox, on_delete=models.SET_NULL, null=True)  # New relationship
    
    class Meta:
        db_table = 'image'
        verbose_name_plural = 'Images'
        
    def __str__(self):
        return self.image_name