import logging
from celery import shared_task
from django.utils import timezone
from .models import PipelineRun, DataSource
from etl_core.extract.s3_extractor import S3Extractor
from etl_core.transform.transformer import DataTransformer
from etl_core.load.postgres_loader import PostgresLoader

logger = logging.getLogger('pipeline')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_etl_pipeline(self, source_id: int):
    source = DataSource.objects.get(pk=source_id)
    run = PipelineRun.objects.create(
        source_name=source.name,
        s3_key=source.s3_prefix,
        status=PipelineRun.Status.RUNNING,
    )
    try:
        extractor = S3Extractor()
        transformer = DataTransformer()
        loader = PostgresLoader()

        files = extractor.list_files(source.s3_prefix)
        total_loaded = 0

        for key in files:
            if source.source_type == DataSource.SourceType.PARQUET:
                df = extractor.read_parquet(key)
            else:
                df = extractor.read_csv(key)

            run.rows_extracted += len(df)
            df = transformer.run(df, source.source_type)
            loaded = loader.load(df, source.target_table)
            total_loaded += loaded
            extractor.upload_processed(df, key.split('/')[-1])

        run.rows_loaded = total_loaded
        run.status = PipelineRun.Status.SUCCESS
        logger.info(f"Pipeline '{source.name}' completed: {total_loaded} rows loaded")

    except Exception as exc:
        run.status = PipelineRun.Status.FAILED
        run.error_message = str(exc)
        logger.error(f"Pipeline '{source.name}' failed: {exc}")
        raise self.retry(exc=exc)

    finally:
        run.completed_at = timezone.now()
        run.save()

    return {'source': source.name, 'rows_loaded': total_loaded}


@shared_task
def run_all_active_pipelines():
    sources = DataSource.objects.filter(is_active=True)
    for source in sources:
        run_etl_pipeline.delay(source.pk)
    logger.info(f"Triggered {sources.count()} pipeline(s)")
