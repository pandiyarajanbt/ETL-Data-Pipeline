from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection
from pipeline.models import PipelineRun


class PipelineSummaryView(APIView):
    """Aggregated stats across all pipeline runs."""

    def get(self, request):
        from django.db.models import Count, Sum, Avg
        stats = PipelineRun.objects.aggregate(
            total_runs=Count('id'),
            total_rows_loaded=Sum('rows_loaded'),
            avg_rows_per_run=Avg('rows_loaded'),
        )
        by_status = (
            PipelineRun.objects
            .values('status')
            .annotate(count=Count('id'))
        )
        return Response({'summary': stats, 'by_status': list(by_status)})


class TableStatsView(APIView):
    """Row counts for all loaded tables."""

    def get(self, request):
        table = request.query_params.get('table')
        if not table:
            return Response({'error': 'table param required'}, status=400)
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")  # noqa: S608
            count = cursor.fetchone()[0]
        return Response({'table': table, 'row_count': count})
