from django.db import models
from projects.models import (
    Project,
    ProjectImage
)

class AnnotationGroup(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='annotation_groups'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'annotation_group'
        verbose_name_plural = "Annotation Groups"

    def __str__(self):
        return f"{self.name} - {self.project.name}"


class AnnotationClass(models.Model):
    annotation_group = models.ForeignKey(
        AnnotationGroup, on_delete=models.CASCADE, related_name='classes'
    )
    class_id = models.PositiveIntegerField()
    name = models.CharField(max_length=255) 
    color = models.CharField(max_length=7, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'annotation_class'
        verbose_name_plural = 'Annotation Classes'
        unique_together = ('annotation_group', 'class_id')

    def __str__(self):
        return f"{self.class_id} - {self.name} ({self.annotation_group.project})"


# Create your models here.
class AnnotationType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., "Bounding Box", "Polygon"
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'annotation_type'
        verbose_name_plural = 'Annotation Types'

    def __str__(self):
        return self.name
    
class Annotation(models.Model):
    project_image = models.ForeignKey(
        ProjectImage, on_delete=models.CASCADE, related_name='annotations'
    )
    annotation_type = models.ForeignKey(
        AnnotationType, on_delete=models.SET_NULL, null=True, related_name='annotations'
    )
    annotation_class = models.ForeignKey(
        AnnotationClass, on_delete=models.CASCADE, related_name='annotations'
    )
    data = models.JSONField()
    annotation_uid = models.CharField(max_length=100, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    reviewed = models.BooleanField(default=False)
    rating = models.ForeignKey(AnnotationClass, on_delete=models.SET_NULL, null=True, blank=True)
    feedback_provided = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'annotation'
        verbose_name_plural = 'Annotations'

    def __str__(self):
        return f"{self.project_image.project.name} - {self.annotation_class.name}"