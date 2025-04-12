from django.db import models
from images.models import (
    Image
)

from organizations.models import (
    Organization
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
    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, related_name="projects"
    )

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

class ProjectImage(models.Model):
    STATUS_CHOICES = [
        ('unannotated', 'Unannotated'),
        ('annotated', 'Annotated'),
        ('reviewed', 'Reviewed'),
        ('dataset', 'Dataset'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_images')
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='projects')
    mode = models.ForeignKey(ImageMode, on_delete=models.CASCADE, blank=True, null=True)
    annotated = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    finalized = models.BooleanField(default=False)
    feedback_provided = models.BooleanField(default=False)
    marked_as_null = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unannotated')
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('project', 'image')
        db_table = 'project_image'
        verbose_name_plural = "Project Images"
        
    def __str__(self):
        return f"{self.project.name} - {self.image.image_name}"
    
class Version(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='versions')
    version_name = models.CharField(max_length=100)
    version_number = models.PositiveIntegerField()  # Incremental version number
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    version_file = models.FileField(upload_to="versions/", null=True, blank=True)

    class Meta:
        db_table = 'version'
        verbose_name_plural = 'Versions'
        unique_together = ('project', 'version_number')
        ordering = ['version_number']

    def __str__(self):
        return f"{self.project.name} - {self.version_name} (v{self.version_number})"



class VersionImage(models.Model):
    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name='version_images')
    project_image = models.ForeignKey(ProjectImage, on_delete=models.RESTRICT, related_name='associated_versions')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('version', 'project_image')
        db_table = 'version_image'
        verbose_name_plural = 'Version Images'

    def __str__(self):
        return f"{self.version.version_name} - {self.project_image.image.image_name}"
