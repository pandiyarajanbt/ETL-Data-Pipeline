from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PipelineRun, DataSource
from .serializers import PipelineRunSerializer, DataSourceSerializer
from .tasks import run_etl_pipeline


class DataSourceViewSet(viewsets.ModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer

    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        source = self.get_object()
        task = run_etl_pipeline.delay(source.pk)
        return Response({'task_id': task.id, 'source': source.name}, status=status.HTTP_202_ACCEPTED)


class PipelineRunViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PipelineRun.objects.all()
    serializer_class = PipelineRunSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        source = self.request.query_params.get('source')
        run_status = self.request.query_params.get('status')
        if source:
            qs = qs.filter(source_name__icontains=source)
        if run_status:
            qs = qs.filter(status=run_status)
        return qs
