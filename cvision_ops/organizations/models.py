from django.db import models

# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name
    