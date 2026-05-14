# Deployment Guide

## Prerequisites

- Docker & Docker Compose installed
- AWS credentials with S3 and EMR access
- A running PostgreSQL instance (or use the Docker Compose one)

---

## Production Deployment

### 1. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
- Set `DEBUG=False`
- Generate a strong `SECRET_KEY`: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- Set `ALLOWED_HOSTS` to your domain
- Fill in all AWS and DB credentials

### 2. Build and start

```bash
docker-compose up --build -d
```

### 3. Initialize database

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Verify services

```bash
docker-compose ps
docker-compose logs web
docker-compose logs celery_worker
```

---

## AWS IAM Permissions

The AWS credentials need the following IAM permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::your-bucket", "arn:aws:s3:::your-bucket/*"]
    },
    {
      "Effect": "Allow",
      "Action": ["elasticmapreduce:AddJobFlowSteps", "elasticmapreduce:DescribeStep"],
      "Resource": "arn:aws:elasticmapreduce:*:*:cluster/*"
    }
  ]
}
```

---

## Scheduling Pipeline Runs

1. Log in to Django Admin at `/admin/`
2. Navigate to **Periodic Tasks** → **Add Periodic Task**
3. Configure:
   - Task: `pipeline.tasks.run_all_active_pipelines`
   - Schedule: Interval (e.g., every 1 hour) or Crontab
4. Save — Celery Beat picks it up automatically

---

## Scaling

| Component | How to scale |
|---|---|
| Celery workers | Increase `--concurrency` or add more worker containers |
| Gunicorn | Increase `--workers` (rule: 2×CPU + 1) |
| PostgreSQL | Use AWS RDS with read replicas |
| Redis | Use AWS ElastiCache |

---

## Monitoring

- Pipeline run history: Django Admin → **Pipeline Runs**
- Celery tasks: Use [Flower](https://flower.readthedocs.io/) — `celery -A etl_pipeline flower`
- Logs: `./logs/etl_pipeline.log`, `./logs/access.log`, `./logs/error.log`

---

## Rollback

```bash
# Stop services
docker-compose down

# Revert to previous image
docker-compose up -d --no-build

# Revert last migration
docker-compose exec web python manage.py migrate <app_name> <previous_migration>
```
