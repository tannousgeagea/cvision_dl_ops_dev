# apps/memberships/models.py
from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project
from organizations.models import Organization
User = get_user_model()

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name

class ProjectMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_memberships")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="members")
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="memberships"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "project")
        db_table = "project_membership"
        verbose_name_plural = "Project Memberships"

    def __str__(self):
        return f"{self.user.username} → {self.project.name} ({self.role.name})"

