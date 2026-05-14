from django.db import models


class AnalyticsReport(models.Model):
    name = models.CharField(max_length=255)
    source_table = models.CharField(max_length=255)
    query = models.TextField()
    last_run_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
