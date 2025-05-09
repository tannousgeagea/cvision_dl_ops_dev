from django.db import models
from tenants.models import EdgeBox, SensorBox
from django.contrib.auth import get_user_model

User = get_user_model()

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
    tags = models.ManyToManyField(
        'Tag',
        through='ImageTag',
        related_name='images',
        blank=True
    )

    class Meta:
        db_table = 'image'
        verbose_name_plural = 'Images'
        
    def __str__(self):
        return self.image_name
    
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name

class ImageTag(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='image_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tagged_images')
    tagged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    tagged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('image', 'tag')
        db_table = 'image_tag'
        verbose_name_plural = 'Image Tags'

    def __str__(self):
        return f"{self.image.image_name} - {self.tag.name}"