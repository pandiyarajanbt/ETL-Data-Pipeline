# ETL Data Pipeline — AWS EMR & PostgreSQL

End-to-end ETL pipeline built with Django, AWS EMR, S3, Pandas, and PostgreSQL. Extracts raw data from multiple upstream S3 sources, applies transformation logic, and loads clean records into PostgreSQL for analytics consumption. Automated scheduled runs via Celery Beat replace manual data-wrangling steps.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | Django 4.2 + Django REST Framework |
| ETL Orchestration | Celery + Redis |
| Scheduling | Celery Beat + django-celery-beat |
| Extraction | AWS S3 (boto3), AWS EMR |
| Transformation | Pandas |
| Storage | PostgreSQL 15 |
| Server | Gunicorn + Nginx |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
ETL-Data-Pipeline/
├── etl_pipeline/          # Django project config
│   ├── settings.py
│   ├── celery.py
│   └── urls.py
├── etl_core/              # ETL engine (framework-agnostic)
│   ├── extract/
│   │   ├── s3_extractor.py    # S3 file extraction
│   │   └── emr_extractor.py   # EMR Spark step submission
│   ├── transform/
│   │   └── transformer.py     # Pandas transformation logic
│   └── load/
│       └── postgres_loader.py # PostgreSQL bulk loader
├── pipeline/              # Django app — pipeline management
│   ├── models.py          # PipelineRun, DataSource
│   ├── tasks.py           # Celery tasks
│   ├── views.py           # REST API endpoints
│   ├── serializers.py
│   ├── admin.py
│   └── management/commands/run_pipeline.py
├── analytics/             # Django app — analytics API
│   ├── views.py
│   └── urls.py
├── nginx/nginx.conf
├── scripts/entrypoint.sh
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── docs/
    ├── architecture.md
    ├── api.md
    └── deployment.md
```

---

## Quick Start

### 1. Clone & configure

```bash
git clone <repo-url>
cd ETL-Data-Pipeline
cp .env.example .env
# Edit .env with your credentials
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

This starts: PostgreSQL, Redis, Django (Gunicorn), Celery Worker, Celery Beat, Nginx.

### 3. Run migrations & create superuser

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 4. Trigger a pipeline manually

```bash
# Via management command
docker-compose exec web python manage.py run_pipeline --source my-source

# Via API
curl -X POST http://localhost/api/pipeline/sources/1/trigger/
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` / `False` |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | PostgreSQL credentials |
| `DB_HOST` / `DB_PORT` | PostgreSQL host/port |
| `AWS_ACCESS_KEY_ID` | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `AWS_REGION` | AWS region (e.g. `us-east-1`) |
| `S3_BUCKET_NAME` | S3 bucket for raw/processed data |
| `S3_RAW_PREFIX` | S3 prefix for raw files (e.g. `raw/`) |
| `S3_PROCESSED_PREFIX` | S3 prefix for processed output |
| `REDIS_URL` | Redis connection URL |
| `EMR_CLUSTER_ID` | EMR cluster ID for Spark steps |

---

## API Endpoints

See [docs/api.md](docs/api.md) for full reference.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/pipeline/sources/` | List data sources |
| POST | `/api/pipeline/sources/` | Create data source |
| POST | `/api/pipeline/sources/{id}/trigger/` | Trigger pipeline run |
| GET | `/api/pipeline/runs/` | List pipeline runs |
| GET | `/api/analytics/summary/` | Aggregated run stats |
| GET | `/api/analytics/table-stats/?table=<name>` | Row count for a table |

---

## Scheduling

Schedules are managed via Django Admin → **Periodic Tasks** (django-celery-beat).

To schedule `run_all_active_pipelines` every hour:
1. Go to `/admin/django_celery_beat/periodictask/`
2. Create a new periodic task pointing to `pipeline.tasks.run_all_active_pipelines`
3. Set interval to 1 hour

---

## Docs

- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)
