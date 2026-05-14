# API Reference

Base URL: `http://localhost/api/`

All endpoints require authentication (Session or Token).

---

## Pipeline — Data Sources

### List sources
```
GET /pipeline/sources/
```
Response: paginated list of `DataSource` objects.

### Create source
```
POST /pipeline/sources/
Content-Type: application/json

{
  "name": "sales-data",
  "s3_prefix": "raw/sales/",
  "source_type": "csv",
  "target_table": "sales_records",
  "is_active": true
}
```

### Trigger pipeline run
```
POST /pipeline/sources/{id}/trigger/
```
Response:
```json
{
  "task_id": "abc123",
  "source": "sales-data"
}
```
Returns `202 Accepted`. Use the `task_id` to monitor via Celery.

---

## Pipeline — Runs

### List runs
```
GET /pipeline/runs/
GET /pipeline/runs/?source=sales&status=SUCCESS
```

Query params:
- `source` — filter by source name (case-insensitive contains)
- `status` — filter by status: `PENDING`, `RUNNING`, `SUCCESS`, `FAILED`

### Get run detail
```
GET /pipeline/runs/{id}/
```
Response:
```json
{
  "id": 1,
  "source_name": "sales-data",
  "s3_key": "raw/sales/",
  "status": "SUCCESS",
  "rows_extracted": 50000,
  "rows_loaded": 49850,
  "error_message": "",
  "emr_step_id": "",
  "started_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:02:30Z"
}
```

---

## Analytics

### Pipeline summary
```
GET /analytics/summary/
```
Response:
```json
{
  "summary": {
    "total_runs": 120,
    "total_rows_loaded": 5000000,
    "avg_rows_per_run": 41666.7
  },
  "by_status": [
    {"status": "SUCCESS", "count": 115},
    {"status": "FAILED", "count": 5}
  ]
}
```

### Table row count
```
GET /analytics/table-stats/?table=sales_records
```
Response:
```json
{
  "table": "sales_records",
  "row_count": 2500000
}
```

---

## Management Command

```bash
# Trigger specific source (async via Celery)
python manage.py run_pipeline --source sales-data

# Trigger all active sources
python manage.py run_pipeline --all

# Run synchronously (no Celery, useful for debugging)
python manage.py run_pipeline --source sales-data --sync
```
