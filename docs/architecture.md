# Architecture

## Overview

```
Upstream Sources (S3)
        │
        ▼
  ┌─────────────┐
  │ S3Extractor │  ← boto3, lists & reads CSV/Parquet files
  └──────┬──────┘
         │  raw DataFrame
         ▼
  ┌──────────────────┐
  │ DataTransformer  │  ← Pandas: dedup, normalize, cast types, drop nulls
  └──────┬───────────┘
         │  clean DataFrame
         ▼
  ┌────────────────┐
  │ PostgresLoader │  ← SQLAlchemy bulk insert (chunksize=1000)
  └──────┬─────────┘
         │
         ▼
   PostgreSQL DB  ←── Analytics API reads here
```

## AWS EMR Integration

For large-scale datasets, `EMRExtractor` submits a Spark step to an existing EMR cluster. The Spark job reads raw data, applies heavy transformations, and writes Parquet output back to S3. The Django pipeline then picks up the processed Parquet files via `S3Extractor.read_parquet()`.

```
EMR Cluster
  └── Spark Step (spark-submit)
        ├── Reads: s3://bucket/raw/
        └── Writes: s3://bucket/processed/
              ▲
              └── S3Extractor.read_parquet() → PostgresLoader
```

## Celery Architecture

```
Celery Beat (scheduler)
    └── run_all_active_pipelines (periodic)
            └── run_etl_pipeline.delay(source_id)  [per source]
                    └── Celery Worker
                            ├── S3Extractor
                            ├── DataTransformer
                            └── PostgresLoader
```

## Data Flow

1. `DataSource` records define S3 prefix, file type, and target PostgreSQL table
2. Celery Beat triggers `run_all_active_pipelines` on schedule
3. Per-source `run_etl_pipeline` task is dispatched to Celery workers
4. Each file under the S3 prefix is extracted, transformed, and loaded
5. Processed files are uploaded back to `S3_PROCESSED_PREFIX`
6. `PipelineRun` records track status, row counts, and errors
7. Analytics API exposes aggregated stats from `PipelineRun` and loaded tables
