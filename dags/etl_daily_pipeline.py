"""
Daily ETL Pipeline DAG
Orchestrates extraction, transformation, and loading of daily data
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.task_group import TaskGroup
import logging

logger = logging.getLogger(__name__)

# Default arguments
default_args = {
    'owner': 'alitaha',
    'depends_on_past': False,
    'email': ['data-eng@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}


def extract_data(**context):
    """Extract data from source systems"""
    execution_date = context['ds']
    logger.info(f"Extracting data for {execution_date}")

    # Simulate data extraction
    extracted_records = 10000
    logger.info(f"Extracted {extracted_records} records")

    # Push to XCom for next task
    context['ti'].xcom_push(key='extracted_records', value=extracted_records)
    return extracted_records


def transform_data(**context):
    """Transform and clean data"""
    ti = context['ti']
    records = ti.xcom_pull(task_ids='extract_data', key='extracted_records')

    logger.info(f"Transforming {records} records")

    # Simulate transformation
    transformed_records = records * 0.95  # Some records filtered out
    logger.info(f"Transformed {transformed_records} records")

    ti.xcom_push(key='transformed_records', value=transformed_records)
    return transformed_records


def load_data(**context):
    """Load data to warehouse"""
    ti = context['ti']
    records = ti.xcom_pull(task_ids='transform_data', key='transformed_records')

    logger.info(f"Loading {records} records to warehouse")

    # Simulate loading
    logger.info("Data loaded successfully")
    return records


def validate_data_quality(**context):
    """Validate data quality after loading"""
    logger.info("Running data quality checks")

    # Quality checks
    checks = {
        'null_check': True,
        'duplicate_check': True,
        'schema_check': True,
        'row_count_check': True
    }

    if all(checks.values()):
        logger.info("All quality checks passed")
        return True
    else:
        raise ValueError("Data quality checks failed")


# Define DAG
with DAG(
    dag_id='etl_daily_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline for data warehouse',
    schedule_interval='0 2 * * *',  # Run at 2 AM daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'daily', 'production'],
) as dag:

    # Task 1: Extract data
    extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
        provide_context=True,
    )

    # Task 2: Transform data
    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True,
    )

    # Task 3: Load data
    load = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
        provide_context=True,
    )

    # Task 4: Data quality validation
    validate = PythonOperator(
        task_id='validate_data_quality',
        python_callable=validate_data_quality,
        provide_context=True,
    )

    # Task 5: Update metadata
    update_metadata = PostgresOperator(
        task_id='update_metadata',
        postgres_conn_id='postgres_default',
        sql="""
            INSERT INTO etl_metadata (dag_id, execution_date, status, records_processed)
            VALUES ('{{ dag.dag_id }}', '{{ ds }}', 'SUCCESS', {{ ti.xcom_pull(task_ids='load_data') }});
        """,
    )

    # Task 6: Send notification
    notify = BashOperator(
        task_id='send_notification',
        bash_command='echo "ETL pipeline completed successfully for {{ ds }}"',
    )

    # Task dependencies
    extract >> transform >> load >> validate >> update_metadata >> notify
