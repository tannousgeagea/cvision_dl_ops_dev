from django.db import models
from images.models import (
    Image
)

# Create your models here.
class ProjectType(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'project_type'
        verbose_name_plural = 'Project Type'
        
    def __str__(self):
        return self.name

class Visibility(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'visibility'
        verbose_name_plural = 'Visibility'

    def __str__(self):
        return self.name
 

class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    project_type = models.ForeignKey(ProjectType, on_delete=models.SET_NULL, null=True)
    last_edited = models.DateTimeField(auto_now=True)
    visibility = models.ForeignKey(Visibility, on_delete=models.SET_DEFAULT, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project"
        verbose_name_plural = 'Projects'

    def __str__(self):
        return f"{self.name} - {self.project_type.name}"
    
class ProjectMetadata(models.Model):
    project = models.ForeignKey(Project, on_delete=models.RESTRICT)
    key = models.CharField(max_length=100)
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'key')
        db_table = 'project_metadata'
        verbose_name_plural = "Project Metadata"

    def __str__(self):
        return f"{self.project.name} - {self.key}: {self.value}"

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_images')
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='projects')
    annotated = models.BooleanField(default=False)
    annotations = models.JSONField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'image')
        db_table = 'project_image'
        verbose_name_plural = "Project Images"
        
    def __str__(self):
        return f"{self.project.name} - {self.image.image_name}"