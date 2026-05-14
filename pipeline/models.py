from django.db import models


class PipelineRun(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    source_name = models.CharField(max_length=255)
    s3_key = models.CharField(max_length=512)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    rows_extracted = models.IntegerField(default=0)
    rows_loaded = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    emr_step_id = models.CharField(max_length=50, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.source_name} | {self.status} | {self.started_at:%Y-%m-%d %H:%M}"


class DataSource(models.Model):
    class SourceType(models.TextChoices):
        CSV = 'csv', 'CSV'
        PARQUET = 'parquet', 'Parquet'
        JSON = 'json', 'JSON'

    name = models.CharField(max_length=255, unique=True)
    s3_prefix = models.CharField(max_length=512)
    source_type = models.CharField(max_length=20, choices=SourceType.choices, default=SourceType.CSV)
    target_table = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
