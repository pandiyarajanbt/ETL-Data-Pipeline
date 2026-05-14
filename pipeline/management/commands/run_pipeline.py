from django.core.management.base import BaseCommand
from pipeline.models import DataSource
from pipeline.tasks import run_etl_pipeline, run_all_active_pipelines


class Command(BaseCommand):
    help = 'Trigger ETL pipeline run for a specific source or all active sources'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, help='DataSource name to run')
        parser.add_argument('--all', action='store_true', help='Run all active sources')
        parser.add_argument('--sync', action='store_true', help='Run synchronously (no Celery)')

    def handle(self, *args, **options):
        if options['all']:
            run_all_active_pipelines.delay()
            self.stdout.write(self.style.SUCCESS('Triggered all active pipelines'))
            return

        name = options.get('source')
        if not name:
            self.stderr.write('Provide --source <name> or --all')
            return

        try:
            source = DataSource.objects.get(name=name, is_active=True)
        except DataSource.DoesNotExist:
            self.stderr.write(f"Active source '{name}' not found")
            return

        if options['sync']:
            run_etl_pipeline(source.pk)
        else:
            run_etl_pipeline.delay(source.pk)

        self.stdout.write(self.style.SUCCESS(f"Pipeline triggered for '{name}'"))
