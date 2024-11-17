from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline, StackedInline
from .models import Tenant, Plant, Domain, EdgeBox

# Inline for Plant in Tenant Admin
class PlantInline(TabularInline):
    model = Plant
    extra = 1  # Number of empty forms to display
    fields = ('plant_name', 'location', 'language', 'is_active')
    show_change_link = True

# Inline for Domain in Tenant Admin
class DomainInline(TabularInline):
    model = Domain
    extra = 1
    fields = ('domain_name',)
    show_change_link = True
    
@admin.register(Tenant)
class TenantAdmin(ModelAdmin):
    list_display = ('tenant_id', 'name', 'default_language', 'is_active', 'created_at')
    list_filter = ('is_active', 'default_language')
    search_fields = ('name', 'tenant_id')
    ordering = ('name',)
    inlines = [PlantInline, DomainInline]  # Include Plant and Domain inlines

@admin.register(Plant)
class PlantAdmin(ModelAdmin):
    list_display = ('tenant', 'plant_name', 'location', 'language', 'is_active', 'created_at')
    list_filter = ('is_active', 'language')
    search_fields = ('plant_name', 'location')
    ordering = ('plant_name',)

@admin.register(Domain)
class DomainAdmin(ModelAdmin):
    list_display = ('tenant', 'domain_name', 'created_at')
    search_fields = ('domain_name',)
    ordering = ('domain_name',)
    
@admin.register(EdgeBox)
class EdgeBoxAdmin(ModelAdmin):
    list_display = ('edge_box_id', 'edge_box_location', 'plant', 'created_at')
    list_filter = ('plant__plant_name',)
    search_fields = ('edge_box_id', 'edge_box_location')