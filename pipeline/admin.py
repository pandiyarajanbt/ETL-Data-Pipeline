from django.contrib import admin
from .models import PipelineRun, DataSource


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'target_table', 'is_active', 'created_at')
    list_filter = ('source_type', 'is_active')
    search_fields = ('name', 'target_table')


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    list_display = ('source_name', 'status', 'rows_extracted', 'rows_loaded', 'started_at', 'completed_at')
    list_filter = ('status', 'source_name')
    readonly_fields = ('started_at', 'completed_at', 'rows_extracted', 'rows_loaded', 'error_message')
