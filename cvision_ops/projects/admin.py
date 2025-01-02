
# Register your models here.
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import ProjectType, Visibility, Project, ProjectMetadata, ProjectImage, ImageMode

@admin.register(ProjectType)
class ProjectTypeAdmin(ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Visibility)
class VisibilityAdmin(ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)


class ProjectMetadataInline(TabularInline):
    model = ProjectMetadata
    extra = 1  # Number of empty rows to display for quick addition
    fields = ('key', 'value')
    readonly_fields = ('created_at',)


class ProjectImageInline(TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'annotated', 'added_at')
    readonly_fields = ('added_at',)


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ('name', 'project_type', 'visibility', 'last_edited', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('project_type', 'visibility', 'created_at', 'last_edited')
    ordering = ('-last_edited',)
    inlines = [ProjectMetadataInline, ProjectImageInline]


@admin.register(ProjectMetadata)
class ProjectMetadataAdmin(ModelAdmin):
    list_display = ('project', 'key', 'value', 'created_at')
    search_fields = ('project__name', 'key', 'value')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(ImageMode)
class ImageModeAdmin(ModelAdmin):
    list_display = ('mode', 'description', 'created_at')
    search_fields = ('mode', 'description')
    list_filter = ('created_at',)

@admin.register(ProjectImage)
class ProjectImageAdmin(ModelAdmin):
    list_display = ('project', 'image', 'annotated', 'added_at')
    search_fields = ('project__name', 'image__image_name')
    list_filter = ('annotated', 'added_at', 'project')
    ordering = ('-added_at',)
