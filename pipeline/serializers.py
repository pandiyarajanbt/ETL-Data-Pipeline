from rest_framework import serializers
from .models import PipelineRun, DataSource


class PipelineRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineRun
        fields = '__all__'
        read_only_fields = ('started_at', 'completed_at', 'rows_extracted', 'rows_loaded', 'error_message')


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = '__all__'
