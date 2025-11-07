# Apache Airflow Data Pipeline Orchestration

Production-ready Apache Airflow DAGs for orchestrating complex data workflows, ETL processes, and data quality checks.

## Features

- Multiple DAG examples for different use cases
- ETL workflow orchestration
- Data quality validation
- Task dependencies and scheduling
- Error handling and retries
- Email/Slack notifications
- Dynamic DAG generation

## Technologies

- Apache Airflow 2.7+
- Python 3.9+
- PostgreSQL (metadata database)
- Docker & Docker Compose

## Project Structure

```
airflow-data-pipeline/
├── dags/
│   ├── etl_daily_pipeline.py      # Daily ETL workflow
│   ├── data_quality_check.py      # Data quality DAG
│   ├── api_ingestion_dag.py       # API data ingestion
│   └── ml_training_pipeline.py    # ML model training
├── plugins/
│   ├── operators/
│   │   └── custom_operators.py    # Custom operators
│   └── sensors/
│       └── custom_sensors.py      # Custom sensors
├── config/
│   ├── docker-compose.yml
│   └── airflow.cfg
├── tests/
├── requirements.txt
└── README.md
```

## Quick Start

1. Start Airflow with Docker:
```bash
docker-compose up -d
```

2. Access Airflow UI:
```
http://localhost:8080
Username: airflow
Password: airflow
```

3. Trigger a DAG:
```bash
airflow dags trigger etl_daily_pipeline
```

## DAGs Overview

### ETL Daily Pipeline
- Extracts data from multiple sources
- Transforms and validates data
- Loads to data warehouse
- Sends success/failure notifications

### Data Quality Check
- Validates data freshness
- Checks row counts and nulls
- Monitors data quality metrics
- Alerts on anomalies

### API Ingestion
- Fetches data from REST APIs
- Handles pagination and rate limiting
- Incremental data loading
- Error handling and retries

## Author

Alitaha Celebi - Data Engineer
